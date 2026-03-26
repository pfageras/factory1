document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("cve-body");
    const lastUpdatedEl = document.getElementById("last-updated");
    const totalEl = document.getElementById("total-count");
    const loadingEl = document.getElementById("loading");

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

    async function loadCves() {
        try {
            const response = await fetch("/api/cves");
            if (!response.ok) throw new Error("HTTP " + response.status);

            const data = await response.json();
            loadingEl.style.display = "none";

            if (data.last_updated) {
                lastUpdatedEl.textContent = "Sist oppdatert: " + formatDate(data.last_updated);
            }
            totalEl.textContent = data.total + " sårbarheter siste 7 dager";

            if (data.cves.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5">Ingen CVE-er funnet.</td></tr>';
                return;
            }

            const fragment = document.createDocumentFragment();
            for (const cve of data.cves) {
                const tr = document.createElement("tr");

                const nvdUrl = "https://nvd.nist.gov/vuln/detail/" + encodeURIComponent(cve.id);

                const score = typeof cve.cvss_score === "number" ? cve.cvss_score.toFixed(1) : "\u2014";

                tr.innerHTML =
                    '<td class="cve-id"><a href="' + escapeHtml(nvdUrl) + '" target="_blank" rel="noopener">' + escapeHtml(cve.id) + "</a></td>" +
                    '<td class="description">' + escapeHtml(truncate(cve.description, 200)) + "</td>" +
                    '<td class="score">' + escapeHtml(score) + "</td>" +
                    '<td><span class="severity ' + severityClass(cve.severity) + '">' + escapeHtml(cve.severity) + "</span></td>" +
                    '<td class="date">' + formatDate(cve.last_modified) + "</td>";

                fragment.appendChild(tr);
            }
            tableBody.appendChild(fragment);
        } catch (err) {
            loadingEl.style.display = "none";
            tableBody.innerHTML = '<tr><td colspan="5" class="error">Kunne ikke laste CVE-data: ' + escapeHtml(err.message) + "</td></tr>";
        }
    }

    loadCves();
});
