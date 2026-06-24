document.addEventListener('DOMContentLoaded', () => {
    // Syntax highlighting
    hljs.highlightAll();

    // Render Mermaid diagrams
    const mermaidBlocks = document.querySelectorAll("pre code.language-mermaid");
    mermaidBlocks.forEach((block) => {
        const div = document.createElement("div");
        div.className = "mermaid";
        div.textContent = block.textContent;
        block.parentElement.replaceWith(div);
    });
    mermaid.initialize({ startOnLoad: true, theme: 'dark' });

    // Stepper logic
    const stepNodes = Array.from(document.querySelectorAll('.step-node'));
    const stepLines = Array.from(document.querySelectorAll('.step-line'));
    const activeIndex = stepNodes.findIndex(node => node.classList.contains('active-step'));

    stepNodes.forEach((node, idx) => {
        if (idx < activeIndex) {
            node.classList.add('completed');
        } else if (idx === activeIndex) {
            node.classList.add('active');
        } else {
            node.classList.add('future');
        }
    });

    stepLines.forEach((line, idx) => {
        if (idx < activeIndex) {
            line.classList.add('completed');
        } else {
            line.classList.add('future');
        }
    });

    // Custom terminal/code container styling
    const preBlocks = document.querySelectorAll('pre');
    preBlocks.forEach((pre) => {
        // Skip if it is a mermaid block
        const code = pre.querySelector('code');
        if (code && code.classList.contains('language-mermaid')) {
            return;
        }

        const isTerminal = code && (
            code.classList.contains('language-bash') || 
            code.classList.contains('language-sh') || 
            code.classList.contains('language-shell') || 
            code.classList.contains('language-cmd')
        );

        // Create container wrapper
        const container = document.createElement('div');
        container.className = isTerminal ? 'terminal-window' : 'code-window';

        // Create title bar
        const titleBar = document.createElement('div');
        titleBar.className = 'window-header';

        // Window controls (dots)
        const dots = document.createElement('div');
        dots.className = 'window-dots';
        dots.innerHTML = '<span class="dot dot-close"></span><span class="dot dot-minimize"></span><span class="dot dot-maximize"></span>';
        titleBar.appendChild(dots);

        // Title text
        const titleText = document.createElement('span');
        titleText.className = 'window-title';
        let lang = 'Code';
        if (code && code.className) {
            const match = code.className.match(/language-(\w+)/);
            if (match) {
                lang = match[1];
                if (lang === 'bash' || lang === 'sh') lang = 'Terminal';
                else lang = lang.toUpperCase();
            }
        }
        titleText.textContent = lang;
        titleBar.appendChild(titleText);

        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = `
            <svg class="copy-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span class="copy-text">Copy</span>
        `;
        titleBar.appendChild(copyBtn);

        // Wrap the pre block
        pre.parentNode.insertBefore(container, pre);
        container.appendChild(titleBar);
        container.appendChild(pre);

        // Copy logic
        copyBtn.addEventListener('click', () => {
            const textToCopy = code ? code.textContent : pre.textContent;
            navigator.clipboard.writeText(textToCopy).then(() => {
                copyBtn.classList.add('copied');
                copyBtn.querySelector('.copy-text').textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                    copyBtn.querySelector('.copy-text').textContent = 'Copy';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });

    // Theme Toggle
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const root = document.documentElement;

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = root.getAttribute('data-theme') || 'dark';
        if (currentTheme === 'dark') {
            root.setAttribute('data-theme', 'light');
        } else {
            root.setAttribute('data-theme', 'dark');
        }
    });

    // Mobile Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('menuBtn');
    const closeBtn = document.getElementById('closeSidebarBtn');

    menuBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
    });

    closeBtn.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });
});
