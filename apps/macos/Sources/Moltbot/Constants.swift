import Foundation

let launchdLabel = "bot.molt.mac"
let gatewayLaunchdLabel = "bot.molt.gateway"
let onboardingVersionKey = "moltbot.onboardingVersion"
let currentOnboardingVersion = 7
let pauseDefaultsKey = "moltbot.pauseEnabled"
let iconAnimationsEnabledKey = "moltbot.iconAnimationsEnabled"
let swabbleEnabledKey = "moltbot.swabbleEnabled"
let swabbleTriggersKey = "moltbot.swabbleTriggers"
let voiceWakeTriggerChimeKey = "moltbot.voiceWakeTriggerChime"
let voiceWakeSendChimeKey = "moltbot.voiceWakeSendChime"
let showDockIconKey = "moltbot.showDockIcon"
let defaultVoiceWakeTriggers = ["clawd", "claude"]
let voiceWakeMaxWords = 32
let voiceWakeMaxWordLength = 64
let voiceWakeSupported: Bool = ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 26

let petEnabledKey = "moltbot.pet.enabled"
let petPositionKey = "moltbot.pet.position"
let petWakeWordPrefixKey = "moltbot.pet.wakeWordPrefix"
