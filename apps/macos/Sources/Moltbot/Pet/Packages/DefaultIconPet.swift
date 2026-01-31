import Foundation
import AppKit
import QuartzCore
import CoreGraphics

/// 默认宠物包 - 使用系统 SF Symbols 图标
final class DefaultIconPet: PetPackage {
    let id = "default-icon-pet"
    let name = "Default Pet"

    func render(in context: CGContext, state: PetState) throws {
        let rect = CGRect(x: 0, y: 0, width: 40, height: 40)

        let iconName: String
        let fillColor: NSColor

        switch state {
        case .idle:
            iconName = "moon.circle.fill"
            fillColor = NSColor.systemBlue
        case .working:
            iconName = "play.circle.fill"
            fillColor = NSColor.systemGreen
        case .error:
            iconName = "exclamationmark.triangle.fill"
            fillColor = NSColor.systemRed
        case .disconnected:
            iconName = "wifi.slash"
            fillColor = NSColor.gray
        case .working(let _, let _):
            iconName = "clock.circle.fill"
            fillColor = NSColor.systemOrange
        }

        fillColor.setFill()
        let backgroundRect = CGRect(x: 5, y: 5, width: 30, height: 30)
        context.addEllipse(in: backgroundRect)
        context.fillPath()

        if let symbol = NSImage(systemSymbolName: iconName, accessibilityDescription: nil) {
            let imageRect = CGRect(x: 10, y: 10, width: 20, height: 20)
            symbol.draw(in: imageRect)
        }
    }

    func idleAnimation() throws -> AnimationSequence {
        let breathe = CABasicAnimation(keyPath: "opacity")
        breathe.fromValue = 0.7
        breathe.toValue = 1.0
        breathe.duration = 1.0
        breathe.autoreverses = true
        breathe.repeatCount = .infinity
        return AnimationSequence(animation: breathe, key: "breathe")
    }

    func workingAnimation() throws -> AnimationSequence {
        let bounce = CABasicAnimation(keyPath: "transform.scale.xy")
        bounce.fromValue = 0.95
        bounce.toValue = 1.05
        bounce.duration = 0.5
        bounce.autoreverses = true
        bounce.repeatCount = .infinity
        return AnimationSequence(animation: bounce, key: "bounce")
    }

    func errorAnimation() throws -> AnimationSequence {
        let shake = CABasicAnimation(keyPath: "transform.rotation.z")
        shake.fromValue = -10
        shake.toValue = 10
        shake.duration = 0.4
        shake.autoreverses = true
        shake.repeatCount = 3
        return AnimationSequence(animation: shake, key: "shake")
    }
}

/// 动画序列描述
struct AnimationSequence {
    let animation: CAAnimation
    let key: String
}
