import '@github/tab-container-element';
import '@github/details-menu-element';
import { listen } from 'quicklink';
import Alpine from 'alpinejs';
import listItem from './components/list-item.js';
import searchResultsPage from './components/search-results-page.js';
import eye from './components/eye.js';

window.addEventListener('load', () => listen());

Alpine.data('listItem', listItem);
Alpine.data('searchResultsPage', searchResultsPage);
Alpine.data('eye', eye);

window.addEventListener('alpine:init', () => {
  Alpine.store('searchQuery', '');
});

Alpine.start();
