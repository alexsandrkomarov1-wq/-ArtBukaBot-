(() => {
  "use strict";
  const host = document.querySelector(".hero-art");
  if (!host || host.dataset.scene3dReady === "true") return;
  host.dataset.scene3dReady = "true";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canvas = document.createElement("canvas");
  canvas.className = "site-3d-canvas";
  canvas.setAttribute("aria-label", "Интерактивная трёхмерная композиция семейного архива");
  canvas.setAttribute("role", "img");
  host.prepend(canvas);

  const fallback = () => {
    canvas.hidden = true;
    host.classList.add("site-3d-fallback");
  };

  import("https://cdn.jsdelivr.net/npm/three@0.185.0/build/three.module.js").then((THREE) => {
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas, alpha: true, antialias: true, powerPreference: "high-performance"
      });
    } catch (error) {
      fallback();
      return;
    }

    renderer.setClearColor(0x000000, 0);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0, 8.6);

    scene.add(new THREE.AmbientLight(0x9dbbff, 1.7));
    const key = new THREE.PointLight(0x6deaff, 95, 18);
    key.position.set(3.4, 2.6, 4);
    scene.add(key);
    const violet = new THREE.PointLight(0x7465ff, 110, 18);
    violet.position.set(-3, -2, 2);
    scene.add(violet);

    const core = new THREE.Group();
    scene.add(core);
    const orb = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.23, 5),
      new THREE.MeshPhysicalMaterial({
        color: 0x536de8, metalness: 0.72, roughness: 0.2,
        clearcoat: 1, clearcoatRoughness: 0.12,
        emissive: 0x18266b, emissiveIntensity: 0.5
      })
    );
    core.add(orb);

    const wire = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.29, 2),
      new THREE.MeshBasicMaterial({ color: 0x9defff, wireframe: true, transparent: true, opacity: 0.42 })
    );
    core.add(wire);

    const ringMaterial = new THREE.MeshStandardMaterial({
      color: 0x83e8ff, metalness: 0.8, roughness: 0.22,
      emissive: 0x235aab, emissiveIntensity: 0.7
    });
    const ringA = new THREE.Mesh(new THREE.TorusGeometry(1.78, 0.018, 12, 180), ringMaterial);
    ringA.rotation.set(1.08, 0.32, 0.25);
    core.add(ringA);
    const ringB = new THREE.Mesh(new THREE.TorusGeometry(2.12, 0.009, 8, 180),
      new THREE.MeshBasicMaterial({ color: 0x8e85ff, transparent: true, opacity: 0.72 }));
    ringB.rotation.set(0.38, 1.05, -0.48);
    core.add(ringB);

    const nodes = new THREE.Group();
    const nodeGeometry = new THREE.SphereGeometry(0.045, 12, 12);
    const nodeMaterial = new THREE.MeshBasicMaterial({ color: 0xb7f6ff });
    for (let i = 0; i < 18; i++) {
      const angle = (i / 18) * Math.PI * 2;
      const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
      node.position.set(Math.cos(angle) * 2.2, Math.sin(angle * 1.7) * 0.65, Math.sin(angle) * 1.35);
      nodes.add(node);
    }
    core.add(nodes);

    const particleCount = 420;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 6;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 5;
    }
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particles = new THREE.Points(particleGeometry,
      new THREE.PointsMaterial({ color: 0x9abaff, size: 0.018, transparent: true, opacity: 0.65 }));
    scene.add(particles);

    let targetX = 0;
    let targetY = 0;
    let pointerX = 0;
    let pointerY = 0;
    const resize = () => {
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();

    host.addEventListener("pointermove", (event) => {
      const bounds = host.getBoundingClientRect();
      pointerX = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
      pointerY = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
    }, { passive: true });
    host.addEventListener("pointerleave", () => { pointerX = 0; pointerY = 0; }, { passive: true });

    let frame = 0;
    renderer.setAnimationLoop((time) => {
      if (document.hidden) return;
      const t = time * 0.00025;
      targetX += (pointerY * 0.22 - targetX) * 0.035;
      targetY += (pointerX * 0.32 - targetY) * 0.035;
      core.rotation.x = targetX + (reducedMotion ? 0 : Math.sin(t) * 0.08);
      core.rotation.y = targetY + (reducedMotion ? 0 : t * 0.55);
      ringA.rotation.z += reducedMotion ? 0 : 0.0015;
      ringB.rotation.x += reducedMotion ? 0 : 0.0008;
      particles.rotation.y = reducedMotion ? 0 : t * 0.12;
      renderer.render(scene, camera);
      frame++;
    });

    window.addEventListener("pagehide", () => {
      observer.disconnect();
      renderer.setAnimationLoop(null);
      renderer.dispose();
      particleGeometry.dispose();
      nodeGeometry.dispose();
      orb.geometry.dispose();
      wire.geometry.dispose();
      ringA.geometry.dispose();
      ringB.geometry.dispose();
    }, { once: true });
  }).catch(fallback);

  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reducedMotion) {
    document.querySelectorAll(".archive-card-link,.family-portrait-card,.status-card").forEach((card) => {
      card.addEventListener("pointermove", (event) => {
        const r = card.getBoundingClientRect();
        const x = (event.clientX - r.left) / r.width - 0.5;
        const y = (event.clientY - r.top) / r.height - 0.5;
        card.style.transform = "perspective(900px) translateY(-5px) rotateX(" + (-y * 4) + "deg) rotateY(" + (x * 5) + "deg)";
      });
      card.addEventListener("pointerleave", () => { card.style.transform = ""; });
    });
  }
})();
