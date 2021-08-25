import '@github/tab-container-element';
import { listen } from 'quicklink';
import Alpine from 'alpinejs';
import listItem from './components/list-item.js';
import search from './components/search.js';

window.addEventListener('load', () => listen());

Alpine.data('listItem', listItem);
Alpine.data('search', search);
Alpine.start();
