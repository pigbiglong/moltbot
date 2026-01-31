import Foundation
import CoreGraphics

/// 宠物扩展管理器，处理宠物包的加载和管理
@MainActor
final class PetExtensionManager {
    static let shared = PetExtensionManager()

    private let logger = Logger(subsystem: "bot.molt", category: "pet.extension")
    private var loadedPackages: [String: PetPackage] = [:]

    func getLoadedPackages() -> [String: PetPackage] {
        loadedPackages
    }

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

    func unloadPackage(id: String) {
        loadedPackages.removeValue(forKey: id)
        logger.debug("package unloaded: \(id)")
    }

    private func loadPetPackage(id: String) throws -> PetPackage {
        throw NSError(domain: "PetExtension", code: 1, userInfo: [NSLocalizedDescriptionKey: "Pet package loading not implemented yet"])
    }
}

protocol PetPackage {
    var id: String { get }
    var name: String { get }
    func render(in context: CGContext, state: PetState) throws
}
