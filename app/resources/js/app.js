import '@github/tab-container-element';
import Alpine from 'alpinejs';
import listItem from './components/list-item.js';

Alpine.data('listItem', listItem);
Alpine.start();
