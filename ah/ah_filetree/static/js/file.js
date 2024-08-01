import { html, css } from './lit-core.min.js';
import { BaseEl } from './base.js';

export class File_ extends BaseEl {
  static properties = {
    name: { type: String },
    path: { type: String }
  };

  static styles = css`
    .file {
      padding: 5px;
      cursor: pointer;
    }
    .file:hover {
      background-color: rgba(200, 200, 200, 0.1)
    }
  `;

  constructor() {
    super();
    this.name = '';
    this.path = '';
  }

  firstUpdated() {
    this.addEventListener('contextmenu', this.handleContextMenu);
  }

  _render() {
    return html`
      <div class="file" @click=${this.handleClick}>
        ${this.name}
      </div>
    `;
  }

  handleClick() {
    this.dispatch('file-selected', { name: this.name, path: this.path });
  }

  handleContextMenu(e) {
    e.preventDefault();
    const fileTree = document.querySelector('file-tree');
    if (!fileTree) {
      console.error('file-tree element not found');
      return;
    }
    const contextMenu = fileTree.getEl('context-menu');
    if (!contextMenu) {
      console.error('context-menu element not found');
      return;
    }
    const menuItems = [{ label: 'Delete', action: () => this.deleteFile() }];
    contextMenu.show(e.clientX, e.clientY, menuItems);
  }

  deleteFile() {
    if (confirm(`Are you sure you want to delete ${this.name}?`)) {
      console.log('Delete file:', this.path);
      // Implement delete functionality
      this.dispatch('file-deleted', { path: this.path });
    }
  }
}

customElements.define('file-', File_);
