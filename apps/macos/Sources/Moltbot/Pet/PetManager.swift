import Foundation
import OSLog

/// 宠物管理器，管理宠物生命周期和状态
actor PetManager {
    static let shared = PetManager()
    private let logger = Logger(subsystem: "bot.molt", category: "pet.manager")

    private var context: PetContext = .init(
        state: .idle,
        runningTasks: [],
        waitingTasks: [],
        lastError: nil,
        lastUpdated: Date()
    )

    /// 获取当前上下文
    func getContext() -> PetContext {
        context
    }

    /// 更新上下文（由 TaskMonitor 调用）
    func updateContext(_ newContext: PetContext) {
        context = newContext
        logger.debug("pet context updated: \(context.state.displayName)")
    }

    /// 清除错误状态
    func clearError() {
        if case .error = context.state {
            context = PetContext(
                state: .idle,
                runningTasks: context.runningTasks,
                waitingTasks: context.waitingTasks,
                lastError: nil,
                lastUpdated: Date()
            )
            logger.debug("pet error cleared")
        }
    }

    /// 处理任务开始事件
    func handleJobStarted(_ job: JobInfo) {
        var running = context.runningTasks
        if !running.contains(where: { $0.id == job.id }) {
            running.append(job)
        }
        updateContext(PetContext(
            state: .working(runningCount: running.count, waitingCount: context.waitingTasks.count),
            runningTasks: running,
            waitingTasks: context.waitingTasks,
            lastError: nil,
            lastUpdated: Date()
        ))
    }

    /// 处理任务完成事件
    func handleJobCompleted(_ jobId: String) {
        let running = context.runningTasks.filter { $0.id != jobId }
        let waiting = context.waitingTasks
        let newState: PetState

        if running.isEmpty && waiting.isEmpty {
            newState = .idle
        } else {
            newState = .working(runningCount: running.count, waitingCount: waiting.count)
        }

        updateContext(PetContext(
            state: newState,
            runningTasks: running,
            waitingTasks: waiting,
            lastError: nil,
            lastUpdated: Date()
        ))
    }

    /// 处理任务失败事件
    func handleJobFailed(_ error: String) {
        updateContext(PetContext(
            state: .error(message: error),
            runningTasks: context.runningTasks,
            waitingTasks: context.waitingTasks,
            lastError: error,
            lastUpdated: Date()
        ))
    }
}
