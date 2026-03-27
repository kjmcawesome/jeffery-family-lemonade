from pathlib import Path
import subprocess
import tempfile

from pypdf import PageObject, PdfReader, PdfWriter, Transformation


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "stand-menu.html"
TMP_POSTER_DIR = ROOT / "tmp" / "pdfs"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_POSTER_DIR.mkdir(parents=True, exist_ok=True)

INTERMEDIATE_PDF_PATH = TMP_POSTER_DIR / "stand-menu.full.pdf"
POSTER_PNG_PATH = TMP_POSTER_DIR / "stand-menu-mockup.png"
PDF_PATH = OUTPUT_DIR / "jeffery-family-lemonade-stand-menu.pdf"
DOWNLOAD_COPY = Path("/Users/kj/Downloads/jeffery-family-lemonade-stand-menu.pdf")

VIEWPORT_WIDTH = "1100"
TARGET_SELECTOR = ".menu-sheet"
LETTER_W = 612
LETTER_H = 792

SWIFT_RENDERER = r'''
import Cocoa
import WebKit

func escapeSelector(_ selector: String) -> String {
    selector
        .replacingOccurrences(of: "\\", with: "\\\\")
        .replacingOccurrences(of: "'", with: "\\'")
}

final class Delegate: NSObject, WKNavigationDelegate {
    let webView: WKWebView
    let htmlURL: URL
    let outputURL: URL
    let selector: String

    init(htmlURL: URL, outputURL: URL, viewportWidth: CGFloat, selector: String) {
        self.htmlURL = htmlURL
        self.outputURL = outputURL
        self.selector = selector
        let config = WKWebViewConfiguration()
        self.webView = WKWebView(
            frame: CGRect(x: 0, y: 0, width: viewportWidth, height: 1400),
            configuration: config
        )
        super.init()
        self.webView.navigationDelegate = self
        self.webView.setValue(false, forKey: "drawsBackground")
    }

    func start() {
        webView.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        let escapedSelector = escapeSelector(selector)
        let js = """
        (() => {
          const el = document.querySelector('\(escapedSelector)');
          if (!el) return null;
          const rect = el.getBoundingClientRect();
          return {
            x: rect.left + window.scrollX,
            y: rect.top + window.scrollY,
            width: rect.width,
            height: rect.height
          };
        })()
        """

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
            webView.evaluateJavaScript(js) { result, error in
                if let error = error {
                    fputs("JavaScript error: \(error)\n", stderr)
                    NSApp.terminate(nil)
                    return
                }

                guard
                    let rect = result as? [String: Any],
                    let x = rect["x"] as? Double,
                    let y = rect["y"] as? Double,
                    let width = rect["width"] as? Double,
                    let height = rect["height"] as? Double
                else {
                    fputs("Could not resolve menu bounds.\n", stderr)
                    NSApp.terminate(nil)
                    return
                }

                let captureBottom = y + height + 40
                if captureBottom > Double(webView.bounds.height) {
                    webView.frame = CGRect(
                        x: 0,
                        y: 0,
                        width: webView.bounds.width,
                        height: captureBottom
                    )
                }

                let config = WKPDFConfiguration()
                config.rect = CGRect(x: x, y: y, width: width, height: height)

                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                    webView.createPDF(configuration: config) { result in
                        switch result {
                        case .success(let data):
                            do {
                                try data.write(to: self.outputURL)
                            } catch {
                                fputs("Write error: \(error)\n", stderr)
                            }
                        case .failure(let error):
                            fputs("PDF error: \(error)\n", stderr)
                        }
                        NSApp.terminate(nil)
                    }
                }
            }
        }
    }
}

let args = CommandLine.arguments
guard args.count >= 5 else {
    fputs("Usage: render.swift <html> <output> <viewport-width> <selector>\n", stderr)
    exit(1)
}

let htmlURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])
let viewportWidth = CGFloat(Double(args[3]) ?? 1100)
let selector = args[4]
let delegate = Delegate(
    htmlURL: htmlURL,
    outputURL: outputURL,
    viewportWidth: viewportWidth,
    selector: selector
)

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
DispatchQueue.main.async {
    delegate.start()
}
app.run()
'''


def render_full_sheet():
    with tempfile.TemporaryDirectory(prefix="lemonade-menu-pdf-") as tmp_dir:
        swift_path = Path(tmp_dir) / "render.swift"
        swift_path.write_text(SWIFT_RENDERER)
        subprocess.run(
            [
                "swift",
                str(swift_path),
                str(HTML_PATH),
                str(INTERMEDIATE_PDF_PATH),
                VIEWPORT_WIDTH,
                TARGET_SELECTOR,
            ],
            check=True,
        )


def fit_to_letter():
    source_page = PdfReader(str(INTERMEDIATE_PDF_PATH)).pages[0]
    src_w = float(source_page.mediabox.width)
    src_h = float(source_page.mediabox.height)
    scale = min(LETTER_W / src_w, LETTER_H / src_h)
    tx = (LETTER_W - (src_w * scale)) / 2
    ty = (LETTER_H - (src_h * scale)) / 2

    target_page = PageObject.create_blank_page(width=LETTER_W, height=LETTER_H)
    target_page.merge_transformed_page(
        source_page,
        Transformation().scale(scale).translate(tx, ty),
    )

    writer = PdfWriter()
    writer.add_page(target_page)
    with PDF_PATH.open("wb") as handle:
      writer.write(handle)

    DOWNLOAD_COPY.write_bytes(PDF_PATH.read_bytes())


def render_preview():
    subprocess.run(
        [
            "sips",
            "-s",
            "format",
            "png",
            str(PDF_PATH),
            "--out",
            str(POSTER_PNG_PATH),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build():
    render_full_sheet()
    fit_to_letter()
    render_preview()
    print(POSTER_PNG_PATH)
    print(PDF_PATH)


if __name__ == "__main__":
    build()
