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
    func updateContext(_ newContext: PetContext) async {
        context = newContext
        logger.debug("pet context updated: \(context.state.displayName)")

        // 通知 PetIntegration 更新 UI 和徽章
        await PetIntegration.shared.updateState()
    }

    /// 清除错误状态
    func clearError() async {
        if case .error = context.state {
            let newContext = PetContext(
                state: .idle,
                runningTasks: context.runningTasks,
                waitingTasks: context.waitingTasks,
                lastError: nil,
                lastUpdated: Date()
            )
            context = newContext
            logger.debug("pet error cleared")
        }
    }

    /// 处理任务开始事件
    func handleJobStarted(_ job: JobInfo) async {
        var running = context.runningTasks
        if !running.contains(where: { $0.id == job.id }) {
            running.append(job)
        }
        let newContext = PetContext(
            state: .working(runningCount: running.count, waitingCount: context.waitingTasks.count),
            runningTasks: running,
            waitingTasks: context.waitingTasks,
            lastError: nil,
            lastUpdated: Date()
        )
        await updateContext(newContext)
    }

    /// 处理任务完成事件
    func handleJobCompleted(_ jobId: String) async {
        let running = context.runningTasks.filter { $0.id != jobId }
        let waiting = context.waitingTasks
        let newState: PetState

        if running.isEmpty && waiting.isEmpty {
            newState = .idle
        } else {
            newState = .working(runningCount: running.count, waitingCount: waiting.count)
        }

        let newContext = PetContext(
            state: newState,
            runningTasks: running,
            waitingTasks: waiting,
            lastError: nil,
            lastUpdated: Date()
        )
        await updateContext(newContext)
    }

    /// 处理任务失败事件
    func handleJobFailed(_ error: String) async {
        let newContext = PetContext(
            state: .error(message: error),
            runningTasks: context.runningTasks,
            waitingTasks: context.waitingTasks,
            lastError: error,
            lastUpdated: Date()
        )
        await updateContext(newContext)
    }
}
