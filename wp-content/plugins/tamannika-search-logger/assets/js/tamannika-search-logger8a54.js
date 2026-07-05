document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("treeSearch");

  if (!searchInput || typeof tamannikaSearchLogger === "undefined") {
    return;
  }

  let debounceTimer = null;
  let lastLoggedKeyword = "";

  function normalizeText(text) {
    return (text || "").toLowerCase().trim();
  }

  function getVisibleResultsCount() {
    const visibleCards = Array.from(document.querySelectorAll(".tree-link")).filter((item) => {
      return window.getComputedStyle(item).display !== "none";
    });

    return visibleCards.length;
  }

  function sendKeywordToServer(keyword, resultsFound) {
    const formData = new FormData();
    formData.append("action", "tamannika_log_search");
    formData.append("nonce", tamannikaSearchLogger.nonce);
    formData.append("keyword", keyword);
    formData.append("page_url", window.location.href);
    formData.append("results_found", resultsFound ? "1" : "0");

    fetch(tamannikaSearchLogger.ajaxUrl, {
      method: "POST",
      body: formData,
      credentials: "same-origin",
    }).catch(function (error) {
      console.error("Tamannika Search Logger error:", error);
    });
  }

  searchInput.addEventListener("input", function () {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(function () {
      const keyword = normalizeText(searchInput.value);

      if (!keyword || keyword.length < Number(tamannikaSearchLogger.minChars || 3)) {
        return;
      }

      const visibleResultsCount = getVisibleResultsCount();
      const resultsFound = visibleResultsCount > 0;

      // Hindari kirim keyword yang sama berturut-turut dalam sesi input yang sama
      if (lastLoggedKeyword === keyword) {
        return;
      }

      lastLoggedKeyword = keyword;
      sendKeywordToServer(keyword, resultsFound);
    }, Number(tamannikaSearchLogger.debounceMs || 1000));
  });
});