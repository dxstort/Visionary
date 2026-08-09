import UIKit
import WebKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else {
            fatalError("No scene")
        }
        window = UIWindow(windowScene: scene)
        window?.rootViewController = VisionaryViewController(scene: scene)
        window?.makeKeyAndVisible()
        return true
    }
}

class VisionaryEngine: NSObject {
    private var webView: WKWebView!
    init(scene: UIWindowScene) {
        super.init()
        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences?.allowsContentJavaScript = true
        webView = WKWebView(frame: scene.screen.bounds, configuration: config)
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        webView.backgroundColor = .black
        let bridge = "window.Visionarys={exec:function(c){try{return eval(c);}catch(e){return 'Error:'+e.message;}},log:function(m){console.log('[V]'+m);return m;}};Visionarys.log('Ready');"
        webView.evaluateJavaScript(bridge, completionHandler: nil)
        webView.load(URLRequest(url: URL(string: "https://www.roblox.com/mobile")!))
    }
    func getWebView() -> WKWebView { return webView }
    func runScript(_ script: String, completion: @escaping (String)->Void) {
        let wrapped = "Visionarys.exec(`\(script.replacingOccurrences(of: "`", with: "\\`"))`)"
        webView.evaluateJavaScript(wrapped) { r, e in completion((r as? String) ?? e?.localizedDescription ?? "Done") }
    }
}

class VisionaryViewController: UIViewController {
    private var engine: VisionaryEngine!
    private var floatBtn: UIButton!
    private var scriptInput: UITextView!
    private var statusLabel: UILabel!
    
    init(scene: UIWindowScene) {
        super.init(nibName: nil, bundle: nil)
        engine = VisionaryEngine(scene: scene)
    }
    required init?(coder: NSCoder) { fatalError() }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        guard let wv = engine?.getWebView() else { return }
        wv.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(wv)
        NSLayoutConstraint.activate([
            wv.topAnchor.constraint(equalTo: view.topAnchor),
            wv.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            wv.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            wv.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
        
        floatBtn = UIButton(type: .custom)
        floatBtn.setTitle("⚡", for: .normal)
        floatBtn.titleLabel?.font = .systemFont(ofSize: 32, weight: .bold)
        floatBtn.backgroundColor = .systemPurple
        floatBtn.layer.cornerRadius = 35
        floatBtn.translatesAutoresizingMaskIntoConstraints = false
        floatBtn.addTarget(self, action: #selector(togglePanel), for: .touchUpInside)
        view.addSubview(floatBtn)
        NSLayoutConstraint.activate([
            floatBtn.widthAnchor.constraint(equalToConstant: 70),
            floatBtn.heightAnchor.constraint(equalToConstant: 70),
            floatBtn.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -20),
            floatBtn.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -40)
        ])
        let pan = UIPanGestureRecognizer(target: self, action: #selector(drag))
        floatBtn.addGestureRecognizer(pan)
        
        scriptInput = UITextView()
        scriptInput.backgroundColor = .black.withAlphaComponent(0.85)
        scriptInput.textColor = .systemGreen
        scriptInput.font = .monospacedSystemFont(ofSize: 16, weight: .regular)
        scriptInput.text = "document.body.style.backgroundColor = '#1a1a2e';"
        scriptInput.layer.cornerRadius = 16
        scriptInput.layer.borderWidth = 2
        scriptInput.layer.borderColor = UIColor.systemPurple.cgColor
        scriptInput.isHidden = true
        scriptInput.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scriptInput)
        NSLayoutConstraint.activate([
            scriptInput.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 20),
            scriptInput.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -20),
            scriptInput.bottomAnchor.constraint(equalTo: floatBtn.topAnchor, constant: -20),
            scriptInput.heightAnchor.constraint(equalToConstant: 200)
        ])
        
        let runBtn = UIButton(type: .system)
        runBtn.setTitle("▶ Execute", for: .normal)
        runBtn.backgroundColor = .systemGreen
        runBtn.setTitleColor(.white, for: .normal)
        runBtn.layer.cornerRadius = 12
        runBtn.translatesAutoresizingMaskIntoConstraints = false
        runBtn.addTarget(self, action: #selector(runScript), for: .touchUpInside)
        view.addSubview(runBtn)
        NSLayoutConstraint.activate([
            runBtn.trailingAnchor.constraint(equalTo: scriptInput.trailingAnchor),
            runBtn.topAnchor.constraint(equalTo: scriptInput.bottomAnchor, constant: 12),
            runBtn.widthAnchor.constraint(equalToConstant: 120),
            runBtn.heightAnchor.constraint(equalToConstant: 48)
        ])
        
        statusLabel = UILabel()
        statusLabel.text = "⚡ Visionarys ready"
        statusLabel.textColor = .systemGreen.withAlphaComponent(0.8)
        statusLabel.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        statusLabel.numberOfLines = 3
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(statusLabel)
        NSLayoutConstraint.activate([
            statusLabel.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 20),
            statusLabel.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            statusLabel.trailingAnchor.constraint(equalTo: floatBtn.leadingAnchor, constant: -20)
        ])
    }
    
    @objc func togglePanel() { scriptInput.isHidden.toggle() }
    @objc func drag(_ g: UIPanGestureRecognizer) {
        let t = g.translation(in: view)
        floatBtn.center = CGPoint(x: floatBtn.center.x + t.x, y: floatBtn.center.y + t.y)
        g.setTranslation(.zero, in: view)
    }
    @objc func runScript() {
        guard let code = scriptInput.text, !code.isEmpty else { return }
        statusLabel.text = "⏳ Running..."
        engine.runScript(code) { [weak self] result in
            DispatchQueue.main.async {
                self?.statusLabel.text = "✅ " + result.prefix(80)
            }
        }
    }
}
