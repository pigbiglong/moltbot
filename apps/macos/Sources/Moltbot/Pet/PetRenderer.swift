import AppKit
import Foundation
import CoreAnimation

/// 宠物渲染层
struct PetLayers {
    var background: CALayer
    var content: CALayer
    var badge: CALayer?
    var bubble: CALayer?
}

/// 宠物渲染器，处理视觉渲染和动画
final class PetRenderer: NSObject {
    private let logger = Logger(subsystem: "bot.molt", category: "pet.renderer")

    private var layers: PetLayers?
    private var currentState: PetState = .idle
    private var animationTimer: Timer?

    /// 获取渲染层
    func getLayers() -> PetLayers? {
        layers
    }

    /// 初始化渲染器
    func setup(in view: NSView) {
        let background = CALayer()
        background.frame = view.bounds
        view.layer = background

        let content = CALayer()
        content.frame = CGRect(x: 20, y: 20, width: 40, height: 40)
        background.addSublayer(content)

        layers = PetLayers(background: background, content: content, badge: nil, bubble: nil)

        renderState(.idle, in: view)
    }

    /// 更新状态并触发动画
    func updateState(_ state: PetState, in view: NSView) {
        currentState = state
        renderState(state, in: view)
        startAnimation(for: state)
    }

    /// 渲染当前状态
    private func renderState(_ state: PetState, in view: NSView) {
        guard let layers = layers else { return }

        CATransaction.begin()
        CATransaction.setAnimationDuration(0.3)

        switch state {
        case .idle:
            layers.content.opacity = 1.0
            layers.content.transform = CATransform3DIdentity
            startBreatheAnimation()

        case .working:
            layers.content.opacity = 1.0
            layers.content.transform = CATransform3DMakeScale(1.1, 1.1, 1.0)
            startBounceAnimation()

        case .error:
            layers.content.opacity = 1.0
            startShakeAnimation()

        case .disconnected:
            layers.content.opacity = 0.5
        }

        CATransaction.commit()
    }

    /// 呼吸动画（idle 状态）
    private func startBreatheAnimation() {
        guard let layers = layers else { return }

        let breathe = CABasicAnimation(keyPath: "opacity")
        breathe.fromValue = 0.7
        breathe.toValue = 1.0
        breathe.duration = 1.0
        breathe.autoreverses = true
        breathe.repeatCount = .infinity
        layers.content.add(breathe, forKey: "breathe")
    }

    /// 弹跳动画（working 状态）
    private func startBounceAnimation() {
        guard let layers = layers else { return }
        layers.content.removeAnimation(forKey: "breathe")

        let bounce = CABasicAnimation(keyPath: "transform.scale.y")
        bounce.fromValue = 0.95
        bounce.toValue = 1.05
        bounce.duration = 0.5
        bounce.autoreverses = true
        bounce.repeatCount = .infinity
        layers.content.add(bounce, forKey: "bounce")
    }

    /// 摇晃动画（error 状态）
    private func startShakeAnimation() {
        guard let layers = layers else { return }
        layers.content.removeAnimation(forKey: "breathe")
        layers.content.removeAnimation(forKey: "bounce")

        let shake = CABasicAnimation(keyPath: "transform.rotation.z")
        shake.fromValue = -10
        shake.toValue = 10
        shake.duration = 0.4
        shake.autoreverses = true
        shake.repeatCount = 3
        layers.content.add(shake, forKey: "shake")
    }

    /// 获取当前渲染状态
    func getCurrentState() -> PetState {
        currentState
    }

    /// 停止所有动画
    func stopAllAnimations() {
        guard let layers = layers else { return }
        layers.content.removeAllAnimations()
        animationTimer?.invalidate()
        animationTimer = nil
    }
}

    /// 更新任务徽章
    func updateBadge(running: Int, waiting: Int) {
        guard let layers = layers else { return }

        if let oldBadge = layers.badge {
            oldBadge.removeFromSuperlayer()
        }

        if running == 0 && waiting == 0 {
            layers.badge = nil
            return
        }

        let badge = CAShapeLayer()
        badge.frame = CGRect(x: 55, y: 5, width: 20, height: 20)
        badge.fillColor = running > 0 ? NSColor.systemGreen.cgColor : NSColor.systemYellow.cgColor
        badge.path = CGPath(ellipseIn: CGRect(x: 0, y: 0, width: 20, height: 20))
        layers.background.addSublayer(badge)

        let textLayer = CATextLayer()
        textLayer.string = String(running > 0 ? running : waiting)
        textLayer.font = NSFont.systemFont(ofSize: 10, weight: .bold)
        textLayer.foregroundColor = NSColor.white.cgColor
        textLayer.alignmentMode = .center
        textLayer.frame = CGRect(x: 0, y: 0, width: 20, height: 20)
        badge.addSublayer(textLayer)

        layers.badge = badge
    }

    /// 隐藏徽章
    func hideBadge() {
        guard let layers = layers, let badge = layers.badge else { return }
        badge.removeFromSuperlayer()
        layers.badge = nil
    }
