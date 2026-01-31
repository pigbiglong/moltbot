import Foundation

/// 宠物状态，反映任务队列状态
enum PetState: Codable, Equatable, Sendable {
    case idle                              // 无任务运行，宠物休息
    case working(runningCount: Int, waitingCount: Int) // 有任务执行中
    case error(message: String)               // 最近任务失败
    case disconnected                       // Gateway 连接断开

    var isWorking: Bool {
        if case .working = self { return true }
        return false
    }

    var error: String? {
        if case .error(let message) = self { return message }
        return nil
    }

    var displayName: String {
        switch self {
        case .idle: return "休息"
        case .working(let r, let w): return "工作中 (\(r) 运行中, \(w) 等待)"
        case .error(let msg): return "错误"
        case .disconnected: return "未连接"
        }
    }
}

/// 任务信息（从 Gateway 同步）
struct JobInfo: Codable, Equatable, Sendable {
    let id: String
    let name: String
    let status: String
}

/// 宠物上下文，包含完整状态信息
struct PetContext: Codable, Equatable, Sendable {
    let state: PetState
    let runningTasks: [JobInfo]
    let waitingTasks: [JobInfo]
    let lastError: String?
    let lastUpdated: Date
}
