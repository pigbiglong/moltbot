import AppKit
import Foundation

/// 宠物交互处理器，处理点击和 Voice Wake 唤醒
@MainActor
final class PetInteractionHandler: NSObject {
    private let logger = Logger(subsystem: "bot.molt", category: "pet.interaction")
    private(set) var isMenuVisible = false

    private let wakeWordPrefixKey = "pet.wakeWordPrefix"
    private(set) var wakeWordPrefix: String = "Pet"

    private weak var window: NSPanel?

    init(window: NSPanel?) {
        self.window = window
        super.init()
        loadWakeWordPrefix()
    }

    private func loadWakeWordPrefix() {
        if let saved = UserDefaults.standard.string(forKey: wakeWordPrefixKey) {
            wakeWordPrefix = saved
        }
    }

    func setWakeWordPrefix(_ prefix: String) {
        wakeWordPrefix = prefix
        UserDefaults.standard.set(prefix, forKey: wakeWordPrefixKey)
    }

    func matchesWakeWord(_ transcript: String) -> Bool {
        let lower = transcript.lowercased().trimmingCharacters(in: .whitespaces)
        return lower.hasPrefix(wakeWordPrefix.lowercased())
    }

    /// 处理左键点击 - 直接打开监控面板
    func handleLeftClick() {
        logger.debug("pet left-clicked, opening jobs panel")
        openJobsPanel()
    }

    /// 处理右键点击 - 显示上下文菜单
    func handleClicked() {
        logger.debug("pet right-clicked, showing menu")
        isMenuVisible = true
        showContextMenu()
    }

    /// 显示上下文菜单
    private func showContextMenu() {
        guard let window = window else { return }

        Task.detached {
            let context = await PetManager.shared.getContext()

            await MainActor.run { [weak window] in
                guard let contentView = window?.contentView else { return }

                let menu = NSMenu()

                // 查看任务
                let viewTasks = NSMenuItem()
                viewTasks.title = "查看任务..."
                viewTasks.action = #selector(self.openJobsPanel)
                viewTasks.keyEquivalent = "p"
                viewTasks.keyEquivalentModifierMask = [.command, .shift]
                menu.addItem(viewTasks)

                menu.addItem(NSMenuItem.separator())

                // 当前状态
                let statusItem = NSMenuItem()
                statusItem.title = "状态: " + context.state.displayName
                statusItem.isEnabled = false
                menu.addItem(statusItem)

                menu.addItem(NSMenuItem.separator())

                // 切换宠物
                let nextPet = NSMenuItem()
                nextPet.title = "切换宠物"
                nextPet.action = #selector(self.nextPetAction)
                nextPet.keyEquivalent = "n"
                nextPet.keyEquivalentModifierMask = [.command, .shift]
                menu.addItem(nextPet)

                menu.addItem(NSMenuItem.separator())

                // 设置
                let settings = NSMenuItem()
                settings.title = "设置..."
                settings.action = #selector(self.openPetSettings)
                menu.addItem(settings)

                // 退出
                let quit = NSMenuItem()
                quit.title = "退出"
                quit.action = #selector(self.quitApp)
                quit.keyEquivalent = "q"
                quit.keyEquivalentModifierMask = [.command]
                menu.addItem(quit)

                menu.popUp(positioning: nil, at: NSPoint(x: 0, y: 0), in: contentView)
            }
        }
    }

    @objc private func openJobsPanel() {
        logger.info("opening jobs panel")

        let gatewayURL = "http://localhost:18789"
        let tokenPath = NSHomeDirectory() + "/.moltbot/gateway-token"

        var jobsURL = gatewayURL + "/jobs"
        var savedToken: String?

        // 读取 token 文件
        if let token = try? String(contentsOfFile: tokenPath, encoding: .utf8) {
            let trimmedToken = token.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmedToken.isEmpty {
                if let encoded = trimmedToken.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
                    jobsURL = gatewayURL + "/jobs?token=" + encoded
                    savedToken = trimmedToken
                    logger.info("using token from \(tokenPath)")
                }
            }
        } else {
            logger.warning("token file not found at \(tokenPath)")
        }

        logger.info("opening: \(jobsURL, privacy: .public)")
        NSWorkspace.shared.open(URL(string: jobsURL)!)

        // 等待页面加载后设置 localStorage
        if let token = savedToken {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
                self?.saveTokenToLocalStorage(token: token)
            }
        }
    }

    /// 将 token 保存到 localStorage
    private func saveTokenToLocalStorage(token: String) {
        // 构造 JavaScript 来设置 localStorage
        let settingsJSON = """
        {"gatewayUrl":"ws://localhost:18789","token":"\(token)","sessionKey":"main","lastActiveSessionKey":"main","theme":"system","chatFocusMode":false,"chatShowThinking":true,"splitRatio":0.6,"navCollapsed":false,"navGroupsCollapsed":{}}
        """

        // 使用 osascript 直接在 Safari 中执行 JavaScript
        let escapedJSON = settingsJSON.replacingOccurrences(of: "\"", with: "\\\"")
        let appleScript = """
        tell application "Safari"
            if (count of windows) > 0 then
                set doc to current tab of front window
                set docURL to URL of doc
                if docURL contains "localhost:18789" then
                    tell doc to do JavaScript "localStorage.setItem('moltbot.control.settings.v1', '\\"\(escapedJSON)\\"')"
                end if
            end if
        end tell
        """

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        process.arguments = ["-e", appleScript]

        do {
            try process.run()
            process.waitUntilExit()
            logger.info("Saved token to Safari localStorage")
        } catch {
            logger.error("Failed to save token to localStorage: \(error.localizedDescription)")
        }
    }

    @objc private func nextPetAction() {
        logger.info("cycling to next pet")
        // TODO: 实现宠物切换
    }

    @objc private func openPetSettings() {
        logger.info("opening settings")
        // TODO: 打开宠物设置窗口
    }

    @objc private func quitApp() {
        logger.info("quitting app")
        NSApplication.shared.terminate(nil)
    }
}
