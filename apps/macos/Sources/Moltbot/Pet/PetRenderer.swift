import AppKit
import Foundation
import QuartzCore
import CoreGraphics

enum PetVisualState {
    case online
    case idle
    case busy
    case offline

    var color: NSColor {
        switch self {
        case .online: return NSColor.systemGreen
        case .idle: return NSColor.systemBlue
        case .busy: return NSColor.systemOrange
        case .offline: return NSColor.systemGray
        }
    }

    var animationType: AnimationType {
        switch self {
        case .online: return .pulse
        case .idle: return .breathe
        case .busy: return .bounce
        case .offline: return .none
        }
    }

    enum AnimationType {
        case none
        case breathe
        case pulse
        case bounce
    }

    static func from(petState: PetState) -> PetVisualState {
        switch petState {
        case .idle: return .idle
        case .working: return .busy
        case .error: return .busy
        case .disconnected: return .offline
        }
    }
}

@MainActor
final class PetRenderer: NSObject {
    private let logger = Logger(subsystem: "bot.molt", category: "pet.renderer")

    private var containerLayer: CALayer?
    private var imageLayer: CALayer?
    private var borderLayer: CALayer?
    private var currentVisualState: PetVisualState = .online
    private var catImage: NSImage?

    private let petSize: CGFloat = 100
    private let borderWidth: CGFloat = 4

    func setup(in view: NSView) {
        let container = CALayer()
        container.frame = CGRect(x: 0, y: 0, width: petSize, height: petSize)
        container.backgroundColor = NSColor.clear.cgColor
        view.layer = container
        containerLayer = container

        loadCatImage()
        setupImageLayer()
        setupBorderLayer()

        renderState(.online)
    }

    private func loadCatImage() {
        let homeDir = NSHomeDirectory()
        let paths = [
            Bundle.main.resourcePath.map { "\($0)/PetIcons/cat-online.png" },
            "Resources/PetIcons/cat-online.png",
            "apps/macos/Resources/PetIcons/cat-online.png",
            "/Users/zyjk/Desktop/project/moltbot/apps/macos/Resources/PetIcons/cat-online.png",
            "\(homeDir)/.moltbot/PetIcons/cat-online.png",
            "\(homeDir)/.clawdbot/PetIcons/cat-online.png",
        ].compactMap { $0 }

        for path in paths {
            if let image = NSImage(contentsOfFile: path) {
                catImage = image
                logger.info("Loaded cat image from: \(path)")
                return
            }
        }

        catImage = createPlaceholderImage()
        logger.warning("Cat image not found, using placeholder")
    }

    private func setupImageLayer() {
        guard let image = catImage, let container = containerLayer else { return }

        let imageLayer = CALayer()
        imageLayer.frame = container.bounds
        imageLayer.contents = image
        imageLayer.contentsGravity = .resizeAspectFill
        imageLayer.masksToBounds = true
        imageLayer.cornerRadius = petSize / 2

        container.addSublayer(imageLayer)
        self.imageLayer = imageLayer
    }

    private func setupBorderLayer() {
        guard let container = containerLayer else { return }

        let border = CALayer()
        border.name = "border"
        border.frame = container.bounds
        border.borderColor = currentVisualState.color.withAlphaComponent(0.9).cgColor
        border.borderWidth = borderWidth
        border.cornerRadius = petSize / 2
        border.shadowColor = currentVisualState.color.withAlphaComponent(0.5).cgColor
        border.shadowOffset = .zero
        border.shadowRadius = 8
        border.shadowOpacity = 0.5

        container.addSublayer(border)
        borderLayer = border
    }

    func updateState(_ state: PetState, in view: NSView) {
        let visualState = PetVisualState.from(petState: state)
        currentVisualState = visualState
        renderState(visualState)
    }

    private func renderState(_ state: PetVisualState) {
        guard let container = containerLayer, let border = borderLayer else { return }

        CATransaction.begin()
        CATransaction.setAnimationDuration(0.3)

        border.borderColor = state.color.withAlphaComponent(0.9).cgColor
        border.shadowColor = state.color.withAlphaComponent(0.5).cgColor

        container.removeAllAnimations()

        switch state.animationType {
        case .none:
            break
        case .breathe:
            startBreatheAnimation(on: container)
        case .pulse:
            startPulseAnimation(on: container)
        case .bounce:
            startBounceAnimation(on: container)
        }

        CATransaction.commit()
    }

    private func startBreatheAnimation(on layer: CALayer) {
        let anim = CABasicAnimation(keyPath: "opacity")
        anim.fromValue = 0.7
        anim.toValue = 1.0
        anim.duration = 1.5
        anim.autoreverses = true
        anim.repeatCount = .infinity
        layer.add(anim, forKey: "breathe")
    }

    private func startPulseAnimation(on layer: CALayer) {
        let anim = CABasicAnimation(keyPath: "transform.scale")
        anim.fromValue = 1.0
        anim.toValue = 1.05
        anim.duration = 2.0
        anim.autoreverses = true
        anim.repeatCount = .infinity
        layer.add(anim, forKey: "pulse")
    }

    private func startBounceAnimation(on layer: CALayer) {
        let anim = CABasicAnimation(keyPath: "transform.scale.y")
        anim.fromValue = 0.95
        anim.toValue = 1.05
        anim.duration = 0.3
        anim.autoreverses = true
        anim.repeatCount = .infinity
        layer.add(anim, forKey: "bounce")
    }

    func stopAllAnimations() {
        containerLayer?.removeAllAnimations()
    }

    private func createPlaceholderImage() -> NSImage {
        let image = NSImage(size: CGSize(width: petSize, height: petSize))
        image.lockFocus()
        NSColor.systemGreen.setFill()
        NSBezierPath(ovalIn: CGRect(x: 0, y: 0, width: petSize, height: petSize)).fill()
        NSColor.white.setFill()
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.alignment = .center
        let attributes: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 30),
            .foregroundColor: NSColor.white,
            .paragraphStyle: paragraphStyle
        ]
        "🐱".draw(at: NSPoint(x: 0, y: petSize/2 - 15), withAttributes: attributes)
        image.unlockFocus()
        return image
    }
}
