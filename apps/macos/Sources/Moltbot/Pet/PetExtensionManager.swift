import Foundation

/// 宠物扩展管理器，处理宠物包的加载和管理
final class PetExtensionManager {
    static let shared = PetExtensionManager()

    private let logger = Logger(subsystem: "bot.molt", category: "pet.extension")
    private var loadedPackages: [String: PetPackage] = [:]

    /// 获取已加载的宠物包
    func getLoadedPackages() -> [String: PetPackage] {
        loadedPackages
    }

    /// 加载宠物包
    func loadPackage(id: String) -> PetPackage? {
        if let existing = loadedPackages[id] {
            logger.debug("package already loaded: \(id)")
            return existing
        }

        guard let petPackage = try? loadPetPackage(id: id) else {
            logger.error("failed to load pet package: \(id)")
            return nil
        }

        loadedPackages[id] = petPackage
        return petPackage
    }

    /// 卸载宠物包
    func unloadPackage(id: String) {
        loadedPackages.removeValue(forKey: id)
        logger.debug("package unloaded: \(id)")
    }

    /// 加载宠物包（占位实现）
    private func loadPetPackage(id: String) throws -> PetPackage {
        throw NSError(domain: "PetExtension", code: 1, userInfo: [NSLocalizedDescriptionKey: "Pet package loading not implemented yet"])
    }
}

/// 宠物包协议
protocol PetPackage {
    var id: String { get }
    var name: String { get }
    func render(in context: CGContext, state: PetState) throws
}
