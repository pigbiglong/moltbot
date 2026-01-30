import AppKit
import Foundation

enum WindowPosition: String, Codable {
    case topLeft = "topLeft"
    case topRight = "topRight"
    case bottomLeft = "bottomLeft"
    case bottomRight = "bottomRight"
}

/// 宠物窗口控制器，管理浮动窗口和位置
final class PetWindowController: NSObject {
    static let shared = PetWindowController()
    private let logger = Logger(subsystem: "bot.molt", category: "pet.window")

    private var window: NSPanel?
    private(set) var currentPosition: WindowPosition = .bottomRight

    private let positionDefaultsKey = "pet.windowPosition"
    private let edgeMargin: CGFloat = 20.0

    private init() {
        super.init()
        loadPosition()
    }

    /// 加载保存的位置偏好
    private func loadPosition() {
        if let raw = UserDefaults.standard.string(forKey: positionDefaultsKey),
           let saved = WindowPosition(rawValue: raw) {
            currentPosition = saved
        }
    }

    /// 保存位置偏好
    private func savePosition() {
        UserDefaults.standard.set(currentPosition.rawValue, forKey: positionDefaultsKey)
    }

    /// 设置窗口位置
    func setPosition(_ position: WindowPosition) {
        currentPosition = position
        savePosition()
        updateWindowPosition()
    }

    /// 创建或更新窗口
    func showWindow() {
        if window == nil {
            createWindow()
        }
        updateWindowPosition()
        window?.orderFront(nil)
    }

    /// 隐藏窗口
    func hideWindow() {
        window?.orderOut(nil)
    }

    /// 创建窗口
    private func createWindow() {
        let panel = NSPanel(
            contentRect: NSRect(x: 0, y: 0, width: 80, height: 80),
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )
        panel.isFloatingPanel = true
        panel.level = .floating
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hidesOnDeactivate = false

        self.window = panel
    }

    /// 计算并设置窗口位置
    private func updateWindowPosition() {
        guard let window = window else { return }

        let screen = NSScreen.main ?? NSScreen.screens.first
        guard let screen = screen else { return }

        let frame = screen.visibleFrame
        let windowSize = window.frame.size

        var origin: NSPoint
        switch currentPosition {
        case .topLeft:
            origin = NSPoint(x: frame.minX + edgeMargin, y: frame.maxY - edgeMargin - windowSize.height)
        case .topRight:
            origin = NSPoint(x: frame.maxX - edgeMargin - windowSize.width, y: frame.maxY - edgeMargin - windowSize.height)
        case .bottomLeft:
            origin = NSPoint(x: frame.minX + edgeMargin, y: frame.minY + edgeMargin)
        case .bottomRight:
            origin = NSPoint(x: frame.maxX - edgeMargin - windowSize.width, y: frame.minY + edgeMargin)
        }

        window.setFrameOrigin(origin)
    }
}
