$(document).ready(function() {
    const themeToggle = $('#theme-toggle');
    const themeIcon = $('#theme-icon');
    const themeCss = $('#theme-css');
    const html = $('html');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    themeToggle.click(function() {
        const currentTheme = html.attr('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
    
    function setTheme(theme) {
        html.attr('data-theme', theme);
        themeCss.attr('href', `/static/css/${theme}-theme.css`);
        
        if (theme === 'dark') {
            themeIcon.removeClass('fa-sun').addClass('fa-moon');
            $('nav').removeClass('navbar-light bg-light').addClass('navbar-dark bg-dark');
            $('footer').removeClass('bg-light').addClass('bg-dark');
        } else {
            themeIcon.removeClass('fa-moon').addClass('fa-sun');
            $('nav').removeClass('navbar-dark bg-dark').addClass('navbar-light bg-light');
            $('footer').removeClass('bg-dark').addClass('bg-light');
        }
    }
});