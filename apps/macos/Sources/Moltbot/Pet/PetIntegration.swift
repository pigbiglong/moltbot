import AppKit
import Foundation

/// 宠物系统集成，协调所有宠物组件
final class PetIntegration {
    static let shared = PetIntegration()

    private let windowController = PetWindowController.shared
    private let renderer = PetRenderer()
    private let taskMonitor = TaskMonitorController()
    private var isActive = false

    /// 启动宠物系统
    func start() {
        guard !isActive else { return }
        isActive = true

        windowController.showWindow()

        if let contentView = windowController.window?.contentView {
            renderer.setup(in: contentView)
        }
    }

    /// 停止宠物系统
    func stop() {
        guard isActive else { return }
        isActive = false

        windowController.hideWindow()
        renderer.stopAllAnimations()
    }

    /// 更新宠物状态
    func updateState() async {
        guard isActive else { return }

        if let contentView = windowController.window?.contentView {
            let context = await PetManager.shared.getContext()
            renderer.updateState(context.state, in: contentView)
        }
    }
}
