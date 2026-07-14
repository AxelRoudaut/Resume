document.addEventListener("DOMContentLoaded", () => {
	const toggle = document.getElementById("nav-toggle");
	const links = document.getElementById("nav-links");

	toggle.addEventListener("click", () => {
		const isOpen = links.classList.toggle("is-open");
		toggle.setAttribute("aria-expanded", String(isOpen));
	});

	links.querySelectorAll("a").forEach((link) => {
		link.addEventListener("click", () => {
			links.classList.remove("is-open");
			toggle.setAttribute("aria-expanded", "false");
		});
	});

	const autoHeight = (iframe) => {
		try {
			iframe.style.height = `${iframe.contentDocument.documentElement.scrollHeight}px`;
		} catch {
			// cross-origin fallback: keep the CSS default height
		}
	};

	document.querySelectorAll(".diagram iframe").forEach((iframe) => {
		const resize = () => autoHeight(iframe);
		iframe.addEventListener("load", resize);
		window.addEventListener("resize", resize);
	});

	// Click-to-zoom lightbox for diagrams
	const lightbox = document.getElementById("lightbox");
	const stage = document.getElementById("lightbox-stage");
	const closeBtn = document.getElementById("lightbox-close");

	if (lightbox && stage && closeBtn) {
		let lastFocused = null;

		const openLightbox = (figure) => {
			const src = figure.querySelector("iframe")?.getAttribute("src");
			if (!src) return;
			lastFocused = figure;

			const native = parseInt(figure.style.maxWidth, 10) || 1600;
			const frame = document.createElement("iframe");
			frame.src = src;
			frame.title = "Enlarged diagram";
			frame.style.width = `min(96vw, ${native}px)`;
			frame.style.height = "80vh";
			frame.addEventListener("load", () => autoHeight(frame));

			stage.replaceChildren(frame);
			lightbox.hidden = false;
			document.body.style.overflow = "hidden";
			closeBtn.focus();
		};

		const closeLightbox = () => {
			lightbox.hidden = true;
			stage.replaceChildren();
			document.body.style.overflow = "";
			if (lastFocused) lastFocused.focus();
		};

		document.querySelectorAll(".diagram").forEach((figure) => {
			figure.tabIndex = 0;
			figure.setAttribute("role", "button");
			figure.setAttribute("aria-label", "Enlarge diagram");
			figure.addEventListener("click", () => openLightbox(figure));
			figure.addEventListener("keydown", (e) => {
				if (e.key === "Enter" || e.key === " ") {
					e.preventDefault();
					openLightbox(figure);
				}
			});
		});

		closeBtn.addEventListener("click", closeLightbox);
		lightbox.addEventListener("click", (e) => {
			if (e.target === lightbox) closeLightbox();
		});
		document.addEventListener("keydown", (e) => {
			if (e.key === "Escape" && !lightbox.hidden) closeLightbox();
		});
	}
});
