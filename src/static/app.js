document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("cve-body");
    const lastUpdatedEl = document.getElementById("last-updated");
    const totalEl = document.getElementById("total-count");
    const loadingEl = document.getElementById("loading");
    const filterBtns = document.querySelectorAll(".filter-btn");

    let currentFilter = "all";

    function severityClass(severity) {
        const s = (severity || "unknown").toLowerCase();
        if (s === "critical") return "severity-critical";
        if (s === "high") return "severity-high";
        if (s === "medium") return "severity-medium";
        if (s === "low") return "severity-low";
        return "severity-unknown";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function formatDate(isoString) {
        const d = new Date(isoString);
        return d.toLocaleDateString("nb-NO", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function truncate(text, maxLength) {
        if (!text || text.length <= maxLength) return text || "";
        return text.substring(0, maxLength) + "...";
    }

    function formatPackages(packages) {
        if (!packages || packages.length === 0) return "\u2014";
        return packages.map(function (p) {
            let text = escapeHtml(p.ecosystem) + ":" + escapeHtml(p.name);
            if (p.vulnerable_range) {
                text += ' <span class="pkg-range">' + escapeHtml(p.vulnerable_range) + "</span>";
            }
            if (p.patched_version) {
                text += ' <span class="pkg-patch">\u2192 ' + escapeHtml(p.patched_version) + "</span>";
            }
            return '<span class="pkg-badge">' + text + "</span>";
        }).join(" ");
    }

    function cveUrl(cve) {
        if (cve.id.startsWith("GHSA-")) {
            return "https://github.com/advisories/" + encodeURIComponent(cve.id);
        }
        return "https://nvd.nist.gov/vuln/detail/" + encodeURIComponent(cve.id);
    }

    async function loadCves(filter) {
        loadingEl.style.display = "block";
        tableBody.innerHTML = "";

        try {
            const response = await fetch("/api/cves?filter=" + encodeURIComponent(filter));
            if (!response.ok) throw new Error("HTTP " + response.status);

            const data = await response.json();
            loadingEl.style.display = "none";

            if (data.last_updated) {
                lastUpdatedEl.textContent = "Sist oppdatert: " + formatDate(data.last_updated);
            }
            totalEl.textContent = data.total + " sårbarheter";

            if (data.cves.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6">Ingen sårbarheter funnet.</td></tr>';
                return;
            }

            const fragment = document.createDocumentFragment();
            for (const cve of data.cves) {
                const tr = document.createElement("tr");
                const url = cveUrl(cve);
                const score = typeof cve.cvss_score === "number" ? cve.cvss_score.toFixed(1) : "\u2014";

                tr.innerHTML =
                    '<td class="cve-id"><a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">' + escapeHtml(cve.id) + "</a></td>" +
                    '<td class="description">' + escapeHtml(truncate(cve.description, 200)) + "</td>" +
                    '<td class="packages">' + formatPackages(cve.packages) + "</td>" +
                    '<td class="score">' + escapeHtml(score) + "</td>" +
                    '<td><span class="severity ' + severityClass(cve.severity) + '">' + escapeHtml(cve.severity) + "</span></td>" +
                    '<td class="date">' + formatDate(cve.last_modified) + "</td>";

                fragment.appendChild(tr);
            }
            tableBody.appendChild(fragment);
        } catch (err) {
            loadingEl.style.display = "none";
            tableBody.innerHTML = '<tr><td colspan="6" class="error">Kunne ikke laste data: ' + escapeHtml(err.message) + "</td></tr>";
        }
    }

    filterBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            filterBtns.forEach(function (b) { b.classList.remove("active"); });
            btn.classList.add("active");
            currentFilter = btn.dataset.filter;
            loadCves(currentFilter);
        });
    });

    loadCves(currentFilter);
});
