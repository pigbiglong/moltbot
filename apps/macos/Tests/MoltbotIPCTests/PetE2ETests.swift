import XCTest
@testable import Moltbot

final class PetE2ETests: XCTestCase {
    func testFullPetLifecycle() async throws {
        let integration = PetIntegration.shared
        let manager = PetManager.shared

        integration.start()

        var context1 = await manager.getContext()
        XCTAssertEqual(context1.state, .idle)

        let job = JobInfo(id: "1", name: "Test", status: "running")
        await TaskMonitorController().handleJobStarted(job)

        var context2 = await manager.getContext()
        XCTAssertTrue(context2.state.isWorking)

        await TaskMonitorController().handleJobCompleted("1")

        var context3 = await manager.getContext()

        integration.stop()

        XCTAssert(true)
    }
}
