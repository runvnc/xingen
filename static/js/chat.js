import { LitElement, html, css } from '/static/js/lit-core.min.js'
import { unsafeHTML } from 'https://unpkg.com/lit-html/directives/unsafe-html.js';
import {BaseEl} from './base.js'

class Chat extends BaseEl {
    static properties = {
      sessionid: { type: String },
      messages: []
     }
  
    static styles = [
    css`
      :host {
        display: block;
      }

      .test {
        color: red;
      }
   `
  ]

    constructor(args) {
      super()
      console.log({args})
      this.messages = []
      console.log('Chat component created')
      console.log(this)
     }

    firstUpdated() {
      console.log('First updated')
      console.log('sessionid: ', this.sessionid)
      this.sse = new EventSource(`/chat/${this.sessionid}/events`)
      this.sse.addEventListener('new_message', this._aiMessage.bind(this))
      this.sse.addEventListener('image', this._imageMsg.bind(this))
      this.sse.addEventListener('partial_command', this._partialCmd.bind(this))
    }

    _addMessage(event) {
      const { content, sender } = event.detail
      this.messages = [...this.messages, { content, sender }]

      console.log(this.messages)
      if (sender === 'user') {
        fetch(`/chat/${this.sessionid}/send`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({ message: content })
        })
      }
    }

    _partialCmd(event) {
      console.log('Event received') 
      console.log(event)
      const data = JSON.parse(event.data)
      if (this.messages[this.messages.length-1].sender != 'ai') {
        this.messages = [...this.messages, { content: '', sender: 'ai' }]
      }

      this.messages[this.messages.length-1].content = data.command + ': ' + data.so_far
      this.requestUpdate()
    }


    _aiMessage(event) {
      console.log('Event received') 
      console.log(event)
      const data = JSON.parse(event.data)
      this.messages = [...this.messages, { content: data.content, sender: 'ai' }]
    }

    _imageMsg(event) {
      console.log('Event received') 
      console.log(event)
      const data = JSON.parse(event.data)
      const html = `<img src="${data.url}" alt="image">`
      this.messages = [...this.messages, { content: html, sender: 'ai' }]
    }


    render() {
      return html`
        <div class="chat-container">
        <div class="chat-container" theme="${this.theme}"> <!-- Pass theme to the container -->
          SessionID: ${this.sessionid}
          <div class="chat-log">
            ${this.messages.map(({ content, sender }) => html`
              <chat-message sender="${sender}" theme="${this.theme}"> <!-- Pass theme to chat-message -->
                ${unsafeHTML(content)}
              </chat-message>
            `)}
          </div>
          <chat-form @addmessage="${this._addMessage}" theme="${this.theme}"></chat-form> <!-- Pass theme to chat-form -->
        </div>
      `
    }
  }

customElements.define('chat-ai', Chat)

