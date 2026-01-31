import AppKit
import Foundation

enum WindowPosition: String, Codable {
    case topLeft = "topLeft"
    case topRight = "topRight"
    case bottomLeft = "bottomLeft"
    case bottomRight = "bottomRight"
    case custom = "custom"
}

/// 自定义宠物视图，处理鼠标事件和拖拽
final class PetView: NSView {
    var onLeftClick: (() -> Void)?
    var onRightClick: (() -> Void)?
    var onDragStart: (() -> Void)?
    var onDragMove: ((NSPoint) -> Void)?
    var onDragEnd: (() -> Void)?

    private var isDragging = false
    private var dragStartPoint: NSPoint = .zero
    private var windowStartFrame: NSRect = .zero

    var acceptsFirstMouse: Bool { true }
    override var isFlipped: Bool { true }

    override func mouseDown(with event: NSEvent) {
        let button = event.buttonNumber
        if button == 0 {
            isDragging = true
            dragStartPoint = event.locationInWindow
            windowStartFrame = window?.frame ?? .zero
            onDragStart?()
        }
    }

    override func mouseDragged(with event: NSEvent) {
        if isDragging {
            let currentPoint = event.locationInWindow
            let dx = currentPoint.x - dragStartPoint.x
            let dy = currentPoint.y - dragStartPoint.y

            if abs(dx) > 2 || abs(dy) > 2 {
                guard let window = window else { return }
                let newOrigin = NSPoint(
                    x: windowStartFrame.origin.x + dx,
                    y: windowStartFrame.origin.y + dy
                )
                window.setFrameOrigin(newOrigin)
                onDragMove?(newOrigin)
            }
        }
    }

    override func mouseUp(with event: NSEvent) {
        let button = event.buttonNumber
        if button == 0 {
            let currentPoint = event.locationInWindow
            let dx = abs(currentPoint.x - dragStartPoint.x)
            let dy = abs(currentPoint.y - dragStartPoint.y)

            if dx < 5 && dy < 5 {
                onLeftClick?()
            }
            onDragEnd?()
        }
        isDragging = false
    }

    override func rightMouseUp(with event: NSEvent) {
        onRightClick?()
    }
}

/// 宠物窗口控制器，管理浮动窗口和位置
@MainActor
final class PetWindowController: NSObject {
    static let shared = PetWindowController()
    private let logger = Logger(subsystem: "bot.molt", category: "pet.window")

    var window: NSPanel?
    private(set) var currentPosition: WindowPosition = .bottomRight

    private let edgeMargin: CGFloat = 20.0
    private var interactionHandler: PetInteractionHandler?
    private var petView: PetView?

    private override init() {
        super.init()
        loadPosition()
    }

    /// 加载保存的位置偏好
    private func loadPosition() {
        if let raw = UserDefaults.standard.string(forKey: petPositionKey),
           let saved = WindowPosition(rawValue: raw) {
            currentPosition = saved
        }
    }

    /// 保存位置偏好
    private func savePosition() {
        UserDefaults.standard.set(currentPosition.rawValue, forKey: petPositionKey)
    }

    /// 设置窗口位置
    func setPosition(_ position: WindowPosition) {
        currentPosition = position
        savePosition()
        updateWindowPosition()
    }

    /// 显示窗口
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

    /// 设置唤醒词前缀
    func setWakeWordPrefix(_ prefix: String) {
        interactionHandler?.setWakeWordPrefix(prefix)
    }

    /// 创建窗口
    private func createWindow() {
        let panel = NSPanel(
            contentRect: CGRect(x: 0, y: 0, width: 120, height: 120),
            styleMask: [.borderless, .nonactivatingPanel, .utilityWindow],
            backing: .buffered,
            defer: false
        )
        panel.isFloatingPanel = true
        panel.level = .popUpMenu
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hidesOnDeactivate = false
        panel.ignoresMouseEvents = false
        panel.hasShadow = true

        let view = PetView(frame: CGRect(x: 0, y: 0, width: 120, height: 120))
        view.onLeftClick = { [weak self] in
            self?.interactionHandler?.handleLeftClick()
        }
        view.onRightClick = { [weak self] in
            self?.interactionHandler?.handleClicked()
        }
        view.onDragStart = { [weak self] in
            self?.currentPosition = .custom
        }
        view.onDragEnd = { [weak self] in
            self?.savePosition()
        }
        petView = view
        panel.contentView = view

        self.window = panel

        interactionHandler = PetInteractionHandler(window: panel)
    }

    /// 计算并设置窗口位置
    private func updateWindowPosition() {
        guard let window = window else { return }

        if currentPosition == .custom {
            return
        }

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
        case .custom:
            return
        }

        window.setFrameOrigin(origin)
    }
}
