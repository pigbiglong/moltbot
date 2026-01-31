import Foundation
import OSLog

/// 任务监控控制器，监听 Gateway 事件并更新宠物状态
final class TaskMonitorController: NSObject {
    private let logger = Logger(subsystem: "bot.molt", category: "pet.taskmonitor")

    /// 处理任务开始事件
    func handleJobStarted(_ job: JobInfo) async {
        logger.info("job started: \(job.name) (\(job.id))")
        await PetManager.shared.handleJobStarted(job)
    }

    /// 处理任务完成事件
    func handleJobCompleted(_ jobId: String) async {
        logger.info("job completed: \(jobId)")
        await PetManager.shared.handleJobCompleted(jobId)
    }

    /// 处理任务失败事件
    func handleJobFailed(_ error: String) async {
        logger.error("job failed: \(error)")
        await PetManager.shared.handleJobFailed(error)
    }

    /// 同步任务列表
    func syncJobList(_ jobs: [JobInfo]) async {
        let running = jobs.filter { $0.status == "running" }
        let waiting = jobs.filter { $0.status == "waiting" }

        let context = await PetManager.shared.getContext()
        let newContext = PetContext(
            state: context.state,
            runningTasks: running,
            waitingTasks: waiting,
            lastError: context.lastError,
            lastUpdated: Date()
        )
        await PetManager.shared.updateContext(newContext)
    }
}
