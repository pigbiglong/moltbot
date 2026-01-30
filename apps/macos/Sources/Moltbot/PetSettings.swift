import SwiftUI

struct PetSettings: View {
    @Bindable var state: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            header
            Divider()
            content
        }
        .formStyle(.grouped)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Pet")
                .font(.title2.weight(.semibold))
            Text("Manage your desktop pet settings.")
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 8)
    }

    private var content: some View {
        Group {
            Toggle("Enable Desktop Pet", isOn: $state.petEnabled)

            if state.petEnabled {
                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    Text("Window Position")
                        .font(.headline)
                        .foregroundStyle(.primary)

                    Picker("Position", selection: $state.petPosition) {
                        Text("Top Left").tag("topLeft")
                        Text("Top Right").tag("topRight")
                        Text("Bottom Left").tag("bottomLeft")
                        Text("Bottom Right").tag("bottomRight")
                    }
                    .pickerStyle(.segmented)

                    .help("Choose corner to display pet")
                }

                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    Text("Voice Wake")
                        .font(.headline)
                        .foregroundStyle(.primary)

                    TextField("Wake word prefix", text: $state.petWakeWordPrefix)
                        .textFieldStyle(.roundedBorder)
                        .help("Say this word followed by a command to wake pet")
                }
            }
        }
    }
}

#if DEBUG
struct PetSettings_Previews: PreviewProvider {
    static var previews: some View {
        PetSettings(state: .preview)
            .previewDisplayName("Pet Settings")
    }
}
#endif
