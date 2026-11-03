import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel='msedge',
        headless=True,
        args=[
            '--enable-webgl',
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--ignore-gpu-blocklist',
            '--ignore-certificate-errors',
            '--no-sandbox'
        ]
    )
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    page.on('console', lambda msg: print('CONSOLE:', msg.type, msg.text))
    page.on('pageerror', lambda err: print('PAGEERROR:', err))
    page.on('requestfailed', lambda req: print('REQFAILED:', req.url, req.failure))
    
    print('Loading https://plotsiris.plotly.app/ ...')
    page.goto('https://plotsiris.plotly.app/', wait_until='networkidle', timeout=60000)
    time.sleep(6)
    page.screenshot(path='test_remote_msedge.png')
    
    has_webgl = page.evaluate("""() => {
        const c = document.createElement('canvas');
        const gl = c.getContext('webgl') || c.getContext('experimental-webgl');
        if (!gl) return false;
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'webgl-present';
    }""")
    print('WebGL renderer:', has_webgl)
    
    map_details = page.evaluate("""() => {
        const mapEl = document.getElementById('main-map');
        if (!mapEl) return 'no main-map';
        return {
            innerHTML_length: mapEl.innerHTML.length,
            canvases: Array.from(mapEl.querySelectorAll('canvas')).map(c => ({
                w: c.width,
                h: c.height,
                style: c.getAttribute('style'),
                className: c.className
            })),
            svgs: mapEl.querySelectorAll('svg').length,
            maplibre: typeof window.maplibregl !== 'undefined'
        };
    }""")
    print('Map details:', map_details)
    
    # Check CCTV stream video tag
    page.locator('#btn-open-cctv').click(force=True)
    time.sleep(3)
    cctv_details = page.evaluate("""() => {
        const video = document.getElementById('camera-stream-video');
        const img = document.getElementById('camera-stream-img');
        return {
            video_src: video ? video.currentSrc || video.src : null,
            video_readyState: video ? video.readyState : null,
            video_error: video && video.error ? video.error.code : null,
            video_networkState: video ? video.networkState : null,
            img_src: img ? img.src : null,
            img_displayed: img ? window.getComputedStyle(img).display : null
        };
    }""")
    print('CCTV details:', cctv_details)
    page.screenshot(path='test_cctv_msedge.png')

    browser.close()
