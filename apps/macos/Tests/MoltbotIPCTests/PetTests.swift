import XCTest
@testable import Moltbot

/// PetManager 单元测试
final class PetManagerTests: XCTestCase {
    func testInitialState() async {
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.state, .idle)
        XCTAssertEqual(context.runningTasks.count, 0)
        XCTAssertEqual(context.waitingTasks.count, 0)
    }

    func testJobStartedUpdatesState() async {
        let job = JobInfo(id: "test-1", name: "Test Job", status: "running")
        await PetManager.shared.handleJobStarted(job)

        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 1)
        XCTAssertTrue(context.state.isWorking)
    }

    func testJobCompletedRemovesFromRunning() async {
        let job1 = JobInfo(id: "test-1", name: "Test Job 1", status: "running")
        let job2 = JobInfo(id: "test-2", name: "Test Job 2", status: "running")

        await PetManager.shared.handleJobStarted(job1)
        await PetManager.shared.handleJobStarted(job2)

        await PetManager.shared.handleJobCompleted("test-1")

        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 1)
        XCTAssertEqual(context.runningTasks.first?.id, "test-2")
    }

    func testAllJobsCompleteReturnsToIdle() async {
        let job = JobInfo(id: "test-1", name: "Test Job", status: "running")
        await PetManager.shared.handleJobStarted(job)

        await PetManager.shared.handleJobCompleted("test-1")

        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.state, .idle)
    }

    func testJobFailedSetsErrorState() async {
        await PetManager.shared.handleJobFailed("Test error")

        let context = await PetManager.shared.getContext()
        if case .error(let message) = context.state {
            XCTAssertEqual(message, "Test error")
        } else {
            XCTFail("State should be error")
        }
    }

    func testClearErrorReturnsToIdle() async {
        let job = JobInfo(id: "test-1", name: "Test Job", status: "running")
        await PetManager.shared.handleJobStarted(job)
        await PetManager.shared.handleJobFailed("Test error")
        await PetManager.shared.clearError()

        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.state, .idle)
    }
}

/// WindowPosition 单元测试
final class WindowPositionTests: XCTestCase {
    func testAllPositionsExist() {
        XCTAssertEqual(WindowPosition.topLeft.rawValue, "topLeft")
        XCTAssertEqual(WindowPosition.topRight.rawValue, "topRight")
        XCTAssertEqual(WindowPosition.bottomLeft.rawValue, "bottomLeft")
        XCTAssertEqual(WindowPosition.bottomRight.rawValue, "bottomRight")
    }

    func testWindowPositionCodable() {
        let positions: [WindowPosition] = [.topLeft, .topRight, .bottomLeft, .bottomRight]

        for position in positions {
            let encoder = JSONEncoder()
            let data = try? encoder.encode(position)
            XCTAssertNotNil(data)

            let decoder = JSONDecoder()
            let decoded = try? decoder.decode(WindowPosition.self, from: data!)
            XCTAssertEqual(position, decoded)
        }
    }

    func testWindowPositionRawValue() {
        XCTAssertEqual(WindowPosition.topLeft.rawValue, "topLeft")
    }
}

/// TaskMonitorController 单元测试
final class TaskMonitorControllerTests: XCTestCase {
    func testHandleJobStarted() async {
        let controller = TaskMonitorController()
        let job = JobInfo(id: "test-1", name: "Test Job", status: "running")
        
        await controller.handleJobStarted(job)
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 1)
        XCTAssertTrue(context.state.isWorking)
    }

    func testHandleJobCompleted() async {
        let controller = TaskMonitorController()
        let job = JobInfo(id: "test-1", name: "Test Job", status: "running")
        
        await controller.handleJobStarted(job)
        await controller.handleJobCompleted("test-1")
        
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 0)
    }

    func testHandleJobFailed() async {
        let controller = TaskMonitorController()
        let errorMessage = "Test failure"
        
        await controller.handleJobFailed(errorMessage)
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.lastError, errorMessage)
    }

    func testSyncJobList() async {
        let controller = TaskMonitorController()
        let jobs = [
            JobInfo(id: "1", name: "Job 1", status: "running"),
            JobInfo(id: "2", name: "Job 2", status: "waiting"),
            JobInfo(id: "3", name: "Job 3", status: "running")
        ]
        
        await controller.syncJobList(jobs)
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 2)
        XCTAssertEqual(context.waitingTasks.count, 1)
    }

    func testSyncJobListWithEmptyJobs() async {
        let controller = TaskMonitorController()
        let jobs: [JobInfo] = []
        
        await controller.syncJobList(jobs)
        let context = await PetManager.shared.getContext()
        XCTAssertEqual(context.runningTasks.count, 0)
        XCTAssertEqual(context.waitingTasks.count, 0)
    }

    func testSyncJobListUpdatesLastUpdated() async {
        let controller = TaskMonitorController()
        let beforeUpdate = await PetManager.shared.getContext()

        try? await Task.sleep(nanoseconds: 10_000_000)
        let jobs = [
            JobInfo(id: "1", name: "Job 1", status: "running"),
            JobInfo(id: "2", name: "Job 2", status: "waiting")
        ]
        
        await controller.syncJobList(jobs)
        let afterUpdate = await PetManager.shared.getContext()

        XCTAssertGreaterThan(afterUpdate.lastUpdated.timeIntervalSince1970, beforeUpdate.lastUpdated.timeIntervalSince1970)
    }
}

/// PetState 单元测试
final class PetStateTests: XCTestCase {
    func testIdleDisplayName() {
        let state = PetState.idle
        XCTAssertEqual(state.displayName, "休息")
    }

    func testWorkingDisplayName() {
        let state = PetState.working(runningCount: 2, waitingCount: 3)
        XCTAssertTrue(state.displayName.contains("2 运行中"))
        XCTAssertTrue(state.displayName.contains("3 等待"))
    }

    func testErrorDisplayName() {
        let state = PetState.error(message: "Test error")
        XCTAssertEqual(state.displayName, "错误")
    }

    func testDisconnectedDisplayName() {
        let state = PetState.disconnected
        XCTAssertEqual(state.displayName, "错误")
    }

    func testWorkingStateIsWorking() {
        let state = PetState.working(runningCount: 1, waitingCount: 0)
        XCTAssertTrue(state.isWorking)
    }

    func testIdleStateIsNotWorking() {
        let state = PetState.idle
        XCTAssertFalse(state.isWorking)
    }

    func testErrorReturnsError() {
        let state = PetState.error(message: "Error")
        if let error = state.error {
            XCTAssertEqual(error, "Error")
        } else {
            XCTFail("Error state should have error")
        }
    }

    func testNonErrorStateReturnsNilError() {
        let state = PetState.idle
        XCTAssertNil(state.error)
    }

    func testJobInfoEquality() {
        let job1 = JobInfo(id: "1", name: "Test", status: "running")
        let job2 = JobInfo(id: "1", name: "Test", status: "running")
        let job3 = JobInfo(id: "2", name: "Test", status: "waiting")
        let job4 = JobInfo(id: "3", name: "Test", status: "failed")

        XCTAssertEqual(job1, job2)
        XCTAssertNotEqual(job1, job3)
        XCTAssertNotEqual(job1, job4)
        XCTAssertEqual(job1, job1)
    }

    func testPetContextCodable() {
        let context = PetContext(
            state: .working(runningCount: 1, waitingCount: 2),
            runningTasks: [JobInfo(id: "1", name: "Job 1", status: "running")],
            waitingTasks: [JobInfo(id: "2", name: "Job 2", status: "waiting")],
            lastError: nil,
            lastUpdated: Date()
        )

        let encoder = JSONEncoder()
        let data = try? encoder.encode(context)
        XCTAssertNotNil(data)

        let decoder = JSONDecoder()
        let decoded = try? decoder.decode(PetContext.self, from: data!)
        XCTAssertEqual(context, decoded)
    }

    func testPetContextEquality() {
        let context1 = PetContext(
            state: .working(runningCount: 1, waitingCount: 2),
            runningTasks: [],
            waitingTasks: [],
            lastError: nil,
            lastUpdated: Date()
        )

        let context2 = PetContext(
            state: .working(runningCount: 1, waitingCount: 2),
            runningTasks: [],
            waitingTasks: [],
            lastError: nil,
            lastUpdated: Date()
        )

        XCTAssertEqual(context1, context2)
    }
}
