/**
 * MapLibre & Plotly Interactive Cursor & Pointer Event Handler
 * Ensures all clickable markers and entities show a pointer hand cursor on hover.
 */

(function () {
    'use strict';

    function attachPlotlyCursorListeners(graphId) {
        const el = document.getElementById(graphId);
        if (!el || !el.on || el._hasPointerAttached) return;

        el._hasPointerAttached = true;

        el.on('plotly_hover', function () {
            const canvas = el.querySelector('canvas.mapboxgl-canvas') || 
                           el.querySelector('canvas.maplibregl-canvas') || 
                           el.querySelector('canvas') || 
                           el;
            if (canvas) {
                canvas.style.cursor = 'pointer';
            }
        });

        el.on('plotly_unhover', function () {
            const canvas = el.querySelector('canvas.mapboxgl-canvas') || 
                           el.querySelector('canvas.maplibregl-canvas') || 
                           el.querySelector('canvas') || 
                           el;
            if (canvas) {
                canvas.style.cursor = '';
            }
        });
    }

    function attachSidebarResizeTriggers() {
        var triggerIds = ['btn-toggle-layer-rail', 'btn-toggle-layers-bar', 'btn-expand-sidebar-tab', 'layers-sidebar-header-title'];
        triggerIds.forEach(function (id) {
            var btn = document.getElementById(id);
            if (btn && !btn._hasResizeListenerAttached) {
                btn._hasResizeListenerAttached = true;
                btn.addEventListener('click', function () {
                    setTimeout(function () {
                        window.dispatchEvent(new Event('resize'));
                        if (window.Plotly) {
                            try {
                                Plotly.Plots.resize('main-map');
                                Plotly.Plots.resize('main-graph');
                            } catch (e) {}
                        }
                    }, 280);
                });
            }
        });
    }

    function attachCameraStreamHooks() {
        const video = document.getElementById('camera-stream-video');
        const img = document.getElementById('camera-stream-img');

        if (video && !video._liveHooksAttached) {
            video._liveHooksAttached = true;

            video.addEventListener('loadedmetadata', function () {
                const src = video.getAttribute('src') || '';
                if (!src) return;
                // Offset local sector clips by wall-clock time so reopening never restarts at 00:00
                if (src.indexOf('/assets/') !== -1 && isFinite(video.duration) && video.duration > 2) {
                    const offset = (Date.now() / 1000) % Math.max(video.duration - 0.5, 1);
                    try {
                        video.currentTime = offset;
                    } catch (e) {}
                }
                const p = video.play();
                if (p && typeof p.catch === 'function') {
                    p.catch(function () {});
                }
            });

            video.addEventListener('error', function () {
                if (!video.getAttribute('src')) return;
                video.style.display = 'none';
                if (img) {
                    img.style.display = 'block';
                }
            });
        }

        if (img && !img._liveHooksAttached) {
            img._liveHooksAttached = true;
            img.addEventListener('error', function () {
                if (img.dataset.fallbackApplied === 'true') return;
                img.dataset.fallbackApplied = 'true';
                img.src = '/assets/surveillance_stream.gif';
            });
            img.addEventListener('load', function () {
                if (img.src && img.src.indexOf('surveillance_stream.gif') === -1) {
                    img.dataset.fallbackApplied = 'false';
                }
            });
        }
    }

    function initPointerHooks() {
        attachPlotlyCursorListeners('main-map');
        attachPlotlyCursorListeners('main-graph');
        attachSidebarResizeTriggers();
        attachCameraStreamHooks();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setInterval(initPointerHooks, 600);
        });
    } else {
        setInterval(initPointerHooks, 600);
    }
})();
