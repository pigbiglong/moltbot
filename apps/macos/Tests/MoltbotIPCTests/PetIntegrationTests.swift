import XCTest
@testable import Moltbot

final class PetIntegrationTests: XCTestCase {
    func testIntegrationStartsPetSystem() async throws {
        let integration = PetIntegration.shared
        
        integration.start()
        
        // Verify window is shown
        // Note: Actual window testing would require NSApplication setup
        XCTAssertNotNil(PetWindowController.shared.window)
    }
}
