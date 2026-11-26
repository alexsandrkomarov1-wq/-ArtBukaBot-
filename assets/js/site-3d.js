(() => {
  "use strict";

  const host = document.querySelector(".hero-art");
  if (!host || host.dataset.scene3dReady === "true") return;
  host.dataset.scene3dReady = "true";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const lowPower = window.matchMedia("(max-width: 700px)").matches ||
    (navigator.deviceMemory && navigator.deviceMemory <= 4) ||
    (navigator.connection && navigator.connection.saveData);
  const createCanvas = () => {
    const element = document.createElement("canvas");
    element.className = "site-3d-canvas";
    element.setAttribute("aria-label", "Трёхмерный интерактивный мир KOMAROVA_CORE с центральным ядром и порталами проектов");
    element.setAttribute("role", "img");
    return element;
  };
  let canvas = createCanvas();
  host.prepend(canvas);

  const setRenderStatus = (label) => {
    const status = document.querySelector("[data-world-render-status]");
    if (status) status.textContent = label;
  };

  const fallback = () => {
    canvas.hidden = true;
    host.classList.add("site-3d-fallback");
    setRenderStatus("3D-графика недоступна · порталы и разделы остаются активны");
  };

  const threeUrl = "https://cdn.jsdelivr.net/npm/three@0.185.0/build/three.module.js";
  const threeWebGPUUrl = "https://cdn.jsdelivr.net/npm/three@0.185.0/build/three.webgpu.js";
  const canAttemptWebGPU = Boolean(window.isSecureContext && navigator.gpu && !lowPower);
  const webgpuModule = canAttemptWebGPU
    ? import(threeWebGPUUrl).catch(() => null)
    : Promise.resolve(null);

  Promise.all([import(threeUrl), webgpuModule]).then(async ([THREE, THREEGPU]) => {
    let renderer = null;
    let graphicsMode = "webgl2";
    let handleWebGPUDeviceLost = null;
    let webgpuLostBeforeRecoveryReady = false;
    let recoveringWebGPU = false;

    if (THREEGPU && THREEGPU.WebGPURenderer && canAttemptWebGPU) {
      try {
        renderer = new THREEGPU.WebGPURenderer({
          canvas,
          alpha: true,
          antialias: true,
          powerPreference: "high-performance"
        });
        await renderer.init();
        graphicsMode = renderer.backend && renderer.backend.isWebGLBackend ? "webgl2" : "webgpu";
        if (graphicsMode === "webgpu" && typeof renderer.onDeviceLost === "function") {
          const defaultDeviceLostHandler = renderer.onDeviceLost.bind(renderer);
          renderer.onDeviceLost = (info) => {
            defaultDeviceLostHandler(info);
            if (info && info.reason === "destroyed") return;
            webgpuLostBeforeRecoveryReady = true;
            if (handleWebGPUDeviceLost) handleWebGPUDeviceLost();
          };
        }
      } catch (error) {
        if (renderer) {
          try { renderer.dispose(); } catch (disposeError) { /* release best-effort */ }
        }
        renderer = null;
        const replacementCanvas = createCanvas();
        canvas.replaceWith(replacementCanvas);
        canvas = replacementCanvas;
      }
    }

    if (!renderer) {
      try {
        renderer = new THREE.WebGLRenderer({
          canvas,
          alpha: true,
          antialias: !lowPower,
          powerPreference: lowPower ? "low-power" : "high-performance",
          failIfMajorPerformanceCaveat: false
        });
        graphicsMode = lowPower ? "lite-3d" : "webgl2";
      } catch (error) {
        fallback();
        return;
      }
    }

    const renderLabels = {
      webgpu: "3D запущено · WebGPU",
      webgl2: "3D запущено · WebGL2",
      "lite-3d": "Облегчённая 3D-сцена · WebGL2"
    };
    setRenderStatus(renderLabels[graphicsMode]);
    renderer.setClearColor(0x000000, 0);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, lowPower ? 1 : 1.45));
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 80);
    camera.position.set(0, 0.15, 9.2);

    scene.add(new THREE.AmbientLight(0xaabfff, 1.25));
    const key = new THREE.PointLight(0x70e4ff, 78, 20);
    key.position.set(3.5, 3, 4);
    scene.add(key);
    const fill = new THREE.PointLight(0x8874ff, 95, 18);
    fill.position.set(-3.5, -1.5, 2);
    scene.add(fill);
    const warm = new THREE.PointLight(0xffd7a0, 24, 12);
    warm.position.set(0, -3, 2);
    scene.add(warm);

    const museum = new THREE.Group();
    scene.add(museum);

    const coreMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x7289ff,
      metalness: 0.62,
      roughness: 0.19,
      transmission: 0.12,
      thickness: 0.7,
      clearcoat: 1,
      clearcoatRoughness: 0.12,
      emissive: 0x273a9b,
      emissiveIntensity: 0.45
    });
    const core = new THREE.Mesh(new THREE.IcosahedronGeometry(0.88, 3), coreMaterial);
    core.position.set(0, 0.05, 0.15);
    museum.add(core);

    const innerCore = new THREE.Mesh(
      new THREE.OctahedronGeometry(0.47, 1),
      new THREE.MeshStandardMaterial({
        color: 0xb4f5ff,
        metalness: 0.8,
        roughness: 0.16,
        emissive: 0x2a9fca,
        emissiveIntensity: 1.1
      })
    );
    innerCore.position.copy(core.position);
    museum.add(innerCore);

    const haloMaterial = new THREE.MeshBasicMaterial({
      color: 0x9beeff,
      transparent: true,
      opacity: 0.7
    });
    const halo = new THREE.Mesh(new THREE.TorusGeometry(1.38, 0.012, 8, 144), haloMaterial);
    halo.rotation.set(1.08, 0.28, 0.22);
    halo.position.copy(core.position);
    museum.add(halo);

    const haloOuter = new THREE.Mesh(
      new THREE.TorusGeometry(1.76, 0.006, 6, 144),
      new THREE.MeshBasicMaterial({ color: 0x988aff, transparent: true, opacity: 0.55 })
    );
    haloOuter.rotation.set(0.38, 1.02, -0.42);
    haloOuter.position.copy(core.position);
    museum.add(haloOuter);

    const archMaterial = new THREE.MeshStandardMaterial({
      color: 0x7a9cff,
      metalness: 0.76,
      roughness: 0.24,
      emissive: 0x283c8a,
      emissiveIntensity: 0.32
    });
    const arch = new THREE.Mesh(
      new THREE.TorusGeometry(3.05, 0.025, 8, 120, Math.PI),
      archMaterial
    );
    arch.position.set(0, -0.18, -1.05);
    arch.rotation.z = Math.PI;
    museum.add(arch);

    const portalAnchors = [...document.querySelectorAll(".world-portals .world-portal")];
    const portalTargets = [];
    const portalGroup = new THREE.Group();
    museum.add(portalGroup);
    const portalPalette = [0x79eaff,0xa7a0ff,0x83f0cf,0xffd28b,0x7bdcff,0xc5a5ff,0x8ce6c1,0xffa9bf];
    portalAnchors.forEach((anchor, index) => {
      const angle = (index / Math.max(1, portalAnchors.length)) * Math.PI * 2 - Math.PI / 2;
      const group = new THREE.Group();
      group.position.set(Math.cos(angle) * 3.15, Math.sin(angle) * 1.72 + 0.08, -0.72);
      group.rotation.z = -angle * 0.08;
      const tint = portalPalette[index % portalPalette.length];
      const glass = new THREE.Mesh(
        new THREE.BoxGeometry(0.78, 0.98, 0.075),
        new THREE.MeshPhysicalMaterial({ color: 0x152c58, metalness: 0.5, roughness: 0.2, transparent: true, opacity: 0.78, clearcoat: 1, emissive: tint, emissiveIntensity: 0.12 })
      );
      glass.userData.portalIndex = index;
      group.add(glass);
      portalTargets.push(glass);
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(0.48, 0.035, 10, 64),
        new THREE.MeshStandardMaterial({ color: tint, metalness: 0.62, roughness: 0.2, emissive: tint, emissiveIntensity: 0.75 })
      );
      ring.position.z = 0.07;
      ring.userData.portalIndex = index;
      group.add(ring);
      portalTargets.push(ring);
      const beacon = new THREE.Mesh(
        new THREE.SphereGeometry(0.075, 14, 14),
        new THREE.MeshBasicMaterial({ color: tint })
      );
      beacon.position.set(0, 0, 0.13);
      group.add(beacon);
      portalGroup.add(group);
    });

    const frameGroup = new THREE.Group();
    museum.add(frameGroup);
    const framePositions = [
      [-2.45, 0.78, -0.25, -0.12],
      [2.45, 0.78, -0.25, 0.12],
      [-2.05, -1.28, -0.35, 0.18],
      [2.05, -1.28, -0.35, -0.18]
    ];
    const frameMaterial = new THREE.MeshStandardMaterial({
      color: 0xc3d5ff,
      metalness: 0.72,
      roughness: 0.22,
      emissive: 0x344f9a,
      emissiveIntensity: 0.38
    });
    const panelMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x24396f,
      metalness: 0.42,
      roughness: 0.28,
      transparent: true,
      opacity: 0.82,
      clearcoat: 1
    });
    framePositions.forEach((p, index) => {
      const group = new THREE.Group();
      group.position.set(p[0], p[1], p[2]);
      group.rotation.z = p[3];
      const panel = new THREE.Mesh(new THREE.BoxGeometry(0.76, 1.02, 0.055), panelMaterial);
      group.add(panel);
      const edge = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(0.84, 1.1, 0.07)),
        new THREE.LineBasicMaterial({ color: index % 2 ? 0x9b8cff : 0x8deeff, transparent: true, opacity: 0.85 })
      );
      group.add(edge);
      const light = new THREE.Mesh(
        new THREE.SphereGeometry(0.075, 12, 12),
        new THREE.MeshBasicMaterial({ color: index % 2 ? 0xc3aaff : 0x9af4ff })
      );
      light.position.set(0, 0, 0.09);
      group.add(light);
      frameGroup.add(group);
    });

    const floor = new THREE.GridHelper(10, 22, 0x6e8cff, 0x344775);
    floor.position.set(0, -2.15, -0.4);
    floor.material.transparent = true;
    floor.material.opacity = 0.2;
    museum.add(floor);

    const particleCount = lowPower ? 90 : 190;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 9;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 5.2;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 4;
    }
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particles = new THREE.Points(
      particleGeometry,
      new THREE.PointsMaterial({ color: 0xb6c9ff, size: lowPower ? 0.022 : 0.026, transparent: true, opacity: 0.62 })
    );
    scene.add(particles);

    let pointerX = 0;
    let pointerY = 0;
    let targetX = 0;
    let targetY = 0;
    let keyboardX = 0;
    let keyboardY = 0;
    const portalRaycaster = new THREE.Raycaster();
    const portalPointer = new THREE.Vector2();
    let hoveredPortal = -1;
    const portalAt = (event, targetCanvas) => {
      const bounds = targetCanvas.getBoundingClientRect();
      if (!bounds.width || !bounds.height || event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) return -1;
      portalPointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
      portalPointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
      portalRaycaster.setFromCamera(portalPointer, camera);
      const hit = portalRaycaster.intersectObjects(portalTargets, false)[0];
      return hit ? hit.object.userData.portalIndex : -1;
    };
    const bindPortalInteractions = (targetCanvas) => {
      targetCanvas.addEventListener("pointermove", (event) => {
        if (event.pointerType === "touch") return;
        const index = portalAt(event, targetCanvas);
        targetCanvas.style.cursor = index >= 0 ? "pointer" : "grab";
        if (index !== hoveredPortal) {
          hoveredPortal = index;
          if (index >= 0 && portalAnchors[index]) {
            const label = portalAnchors[index].querySelector("strong");
            setRenderStatus("Портал: " + (label ? label.textContent : "раздел") + " · нажмите для входа");
          }
        }
      }, { passive: true });
      targetCanvas.addEventListener("click", (event) => {
        const index = portalAt(event, targetCanvas);
        if (index < 0 || !portalAnchors[index]) return;
        portalAnchors[index].click();
      });
    };
    bindPortalInteractions(canvas);
    host.addEventListener("keydown", (event) => {
      if (event.target !== host) return;
      const keyName = event.key.toLowerCase();
      if (["arrowup","w"].includes(keyName)) keyboardX = -0.22;
      else if (["arrowdown","s"].includes(keyName)) keyboardX = 0.22;
      else if (["arrowleft","a"].includes(keyName)) keyboardY = -0.28;
      else if (["arrowright","d"].includes(keyName)) keyboardY = 0.28;
      else if (keyName === "+" || keyName === "=") camera.position.z = Math.max(6.2, camera.position.z - 0.45);
      else if (keyName === "-" || keyName === "_") camera.position.z = Math.min(13.5, camera.position.z + 0.45);
      else if (/^[1-8]$/.test(keyName)) {
        const anchor = portalAnchors[Number(keyName) - 1];
        if (anchor) anchor.click();
      } else return;
      event.preventDefault();
    });
    host.addEventListener("keyup", (event) => {
      const keyName = event.key.toLowerCase();
      if (["arrowup","arrowdown","w","s"].includes(keyName)) keyboardX = 0;
      if (["arrowleft","arrowright","a","d"].includes(keyName)) keyboardY = 0;
    });
    window.addEventListener("blur", () => { keyboardX = 0; keyboardY = 0; });
    let visible = true;
    const resize = () => {
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
    resize();

    const visibilityObserver = new IntersectionObserver((entries) => {
      visible = Boolean(entries[0] && entries[0].isIntersecting);
    }, { threshold: 0.05 });
    visibilityObserver.observe(host);

    host.addEventListener("pointermove", (event) => {
      const bounds = host.getBoundingClientRect();
      pointerX = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
      pointerY = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
    }, { passive: true });
    host.addEventListener("pointerleave", () => {
      pointerX = 0;
      pointerY = 0;
    }, { passive: true });

    const renderFrame = (time) => {
      if (document.hidden || !visible) return;
      const t = time * 0.00022;
      targetX += (pointerY * 0.13 + keyboardX - targetX) * 0.035;
      targetY += (pointerX * 0.2 + keyboardY - targetY) * 0.035;
      museum.rotation.x = targetX + (reducedMotion ? 0 : Math.sin(t) * 0.025);
      museum.rotation.y = targetY + (reducedMotion ? 0 : Math.sin(t * 0.7) * 0.045);
      if (!reducedMotion) {
        core.rotation.y = t * 0.42;
        core.rotation.x = Math.sin(t * 0.8) * 0.12;
        innerCore.rotation.x = -t * 0.55;
        innerCore.rotation.y = t * 0.7;
        halo.rotation.z += 0.0008;
        haloOuter.rotation.x += 0.00045;
        frameGroup.children.forEach((frame, index) => {
          frame.position.y = framePositions[index][1] + Math.sin(t * 1.5 + index) * 0.045;
        });
        particles.rotation.y = t * 0.08;
        portalGroup.children.forEach((portal, index) => { portal.rotation.y = Math.sin(t + index * 0.8) * 0.07; portal.scale.setScalar(1 + Math.sin(t * 1.7 + index) * 0.025); });
      }
      renderer.render(scene, camera);
    };

    handleWebGPUDeviceLost = () => {
      if (recoveringWebGPU || graphicsMode !== "webgpu" || !renderer) return;
      recoveringWebGPU = true;
      const previousRenderer = renderer;
      const replacementCanvas = createCanvas();
      canvas.replaceWith(replacementCanvas);
      canvas = replacementCanvas;
      bindPortalInteractions(canvas);
      canvas.addEventListener("webglcontextlost", (event) => {
        event.preventDefault();
        if (renderer) renderer.setAnimationLoop(null);
        fallback();
      }, { once: true });
      try {
        const replacementRenderer = new THREE.WebGLRenderer({
          canvas,
          alpha: true,
          antialias: !lowPower,
          powerPreference: lowPower ? "low-power" : "high-performance",
          failIfMajorPerformanceCaveat: false
        });
        replacementRenderer.setClearColor(0x000000, 0);
        replacementRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, lowPower ? 1 : 1.45));
        replacementRenderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer = replacementRenderer;
        graphicsMode = lowPower ? "lite-3d" : "webgl2";
        resize();
        setRenderStatus("WebGPU остановлен · автоматический переход на " + (lowPower ? "Lite 3D" : "WebGL2"));
        replacementRenderer.setAnimationLoop(renderFrame);
        try {
          previousRenderer.setAnimationLoop(null);
          previousRenderer.dispose();
        } catch (disposeError) {
          /* release best-effort after device loss */
        }
      } catch (error) {
        try {
          previousRenderer.setAnimationLoop(null);
          previousRenderer.dispose();
        } catch (disposeError) {
          /* release best-effort after device loss */
        }
        fallback();
      } finally {
        recoveringWebGPU = false;
      }
    };

    if (webgpuLostBeforeRecoveryReady) {
      handleWebGPUDeviceLost();
    } else {
      renderer.setAnimationLoop(renderFrame);
    }

    canvas.addEventListener("webglcontextlost", (event) => {
      event.preventDefault();
      if (renderer) renderer.setAnimationLoop(null);
      fallback();
    }, { once: true });

    window.addEventListener("pagehide", () => {
      visibilityObserver.disconnect();
      resizeObserver.disconnect();
      renderer.setAnimationLoop(null);
      renderer.dispose();
      particleGeometry.dispose();
      museum.traverse((object) => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) object.material.forEach((material) => material.dispose());
          else object.material.dispose();
        }
      });
    }, { once: true });
  }).catch(fallback);

  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reducedMotion) {
    document.querySelectorAll(".archive-card-link,.family-portrait-card,.status-card").forEach((card) => {
      card.addEventListener("pointermove", (event) => {
        const bounds = card.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width - 0.5;
        const y = (event.clientY - bounds.top) / bounds.height - 0.5;
        card.style.transform = "perspective(900px) translateY(-5px) rotateX(" + (-y * 3) + "deg) rotateY(" + (x * 4) + "deg)";
      });
      card.addEventListener("pointerleave", () => { card.style.transform = ""; });
    });
  }
})();
