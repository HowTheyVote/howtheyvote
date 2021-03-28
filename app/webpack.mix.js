const mix = require('laravel-mix');

mix.postCss('resources/css/app.css', 'public/css').version();
