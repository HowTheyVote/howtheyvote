import '@github/tab-container-element';
import Alpine from 'alpinejs';
import listItem from './components/list-item.js';
import search from './components/search.js';

Alpine.data('listItem', listItem);
Alpine.data('search', search);
Alpine.start();
