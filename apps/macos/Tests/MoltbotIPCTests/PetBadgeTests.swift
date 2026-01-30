import XCTest
@testable import Moltbot

final class PetBadgeTests: XCTestCase {
    func testBadgeShowsRunningCount() throws {
        let renderer = PetRenderer()
        let testView = NSView(frame: NSRect(x: 0, y: 0, width: 100, height: 100))
        renderer.setup(in: testView)
        
        renderer.updateBadge(running: 2, waiting: 0)
        
        XCTAssertNotNil(renderer.getLayers()?.badge)
    }
}
