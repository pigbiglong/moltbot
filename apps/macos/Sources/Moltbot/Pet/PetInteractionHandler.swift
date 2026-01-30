import AppKit
import Foundation

/// 宠物交互处理器，处理点击和 Voice Wake 唤醒
final class PetInteractionHandler: NSObject {
    private let logger = Logger(subsystem: "bot.molt", category: "pet.interaction")
    private(set) var isMenuVisible = false

    private let wakeWordPrefixKey = "pet.wakeWordPrefix"
    private(set) var wakeWordPrefix: String = "Pet"

    private weak var window: NSPanel?

    /// 初始化
    init(window: NSPanel?) {
        super.init(window: window)
        loadWakeWordPrefix()
    }

    /// 加载唤醒词前缀
    private func loadWakeWordPrefix() {
        if let saved = UserDefaults.standard.string(forKey: wakeWordPrefixKey) {
            wakeWordPrefix = saved
        }
    }

    /// 设置唤醒词前缀
    func setWakeWordPrefix(_ prefix: String) {
        wakeWordPrefix = prefix
        UserDefaults.standard.set(prefix, forKey: wakeWordPrefixKey)
    }

    /// 匹配唤醒词
    func matchesWakeWord(_ transcript: String) -> Bool {
        let lower = transcript.lowercased().trimmingCharacters(in: .whitespaces)
        return lower.hasPrefix(wakeWordPrefix.lowercased())
    }

    /// 处理点击事件
    func handleClicked() {
        logger.debug("pet clicked, showing menu")
        isMenuVisible = true
        showContextMenu()
    }

    /// 显示上下文菜单
    private func showContextMenu() {
        guard let window = window else { return }

        let menu = NSMenu()

        let viewTasks = NSMenuItem(
            title: "查看任务...",
            action: #selector(openJobsPanel),
            keyEquivalent: "p",
            modifierMask: [.command, .shift]
        )
        menu.addItem(viewTasks)

        menu.addItem(NSMenuItem.separator())

        let context = Task { await PetManager.shared.getContext() }
        let statusItem = NSMenuItem(
            title: context.state.displayName,
            action: nil
        )
        statusItem.isEnabled = false
        menu.addItem(statusItem)

        menu.addItem(NSMenuItem.separator())

        let nextPet = NSMenuItem(
            title: "切换宠物",
            action: #selector(nextPetAction),
            keyEquivalent: "n",
            modifierMask: [.command, .shift]
        )
        menu.addItem(nextPet)

        menu.addItem(NSMenuItem.separator())

        let settings = NSMenuItem(
            title: "设置...",
            action: #selector(openPetSettings)
        )
        menu.addItem(settings)

        NSMenu.popUpContextMenu(menu, with: window.frame, forView: window.contentView)
    }

    @objc private func openJobsPanel() {
        logger.info("opening jobs panel from pet menu")
    }

    @objc private func nextPetAction() {
        logger.info("cycling to next pet")
    }

    @objc private func openPetSettings() {
        logger.info("opening pet settings")
    }
}
