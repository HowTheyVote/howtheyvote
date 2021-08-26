import '@github/tab-container-element';
import { listen } from 'quicklink';
import Alpine from 'alpinejs';
import listItem from './components/list-item.js';
import searchResultsPage from './components/search-results-page.js';

window.addEventListener('load', () => listen());

Alpine.data('listItem', listItem);
Alpine.data('searchResultsPage', searchResultsPage);

window.addEventListener('alpine:init', () => {
  Alpine.store('searchQuery', '');
});

Alpine.start();
