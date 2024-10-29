const https = require('node:https')

function httpGet(url, options) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, options, (res) => {
      let data = ''

      res.on('data', (chunk) => {
        data += chunk
      })
      res.on('end', () => {
        resolve(data)
      })

      if (res.statusCode && res.statusCode >= 400) {
        reject(res)
      }
    })

    req.on('error', (err) => {
      reject(err)
    })
  })
}

function httpPost(url, options, payload) {
  const mergedOptions = {
    ...(options || {}),
    method: 'POST',
  }

  return new Promise((resolve, reject) => {
    const req = https.request(url, mergedOptions, (res) => {
      res.setEncoding('utf8')

      let responseBody = ''

      res.on('data', (chunk) => {
        if (typeof chunk === 'string') {
          responseBody += chunk
        }
      })

      res.on('end', () => {
        resolve(responseBody)
      })

      if (res.statusCode && res.statusCode >= 400) {
        reject(res)
      }
    })

    req.on('error', (err) => {
      reject(err)
    })

    let finalPayload = payload

    if (mergedOptions?.headers?.['Content-Type'] === 'application/json' && typeof payload === 'object') {
      finalPayload = JSON.stringify(payload)
    }

    req.write(finalPayload)
    req.end()
  })
}

function makeLarkMessage(title, content, footer, link) {
  return {
    msg_type: 'interactive',
    card: {
      header: {
        title: {
          tag: 'plain_text',
          content: title,
        },
      },
      elements: [{
        tag: 'div',
        text: {
          tag: 'lark_md',
          content,
        },
      }, {
        tag: 'action',
        actions: [
          {
            tag: 'button',
            text: {
              tag: 'lark_md',
              content: footer,
            },
            url: link,
            type: 'default',
            value: {},
          },
        ],
      }],
    },
  }
}

module.exports = {
  httpGet,
  httpPost,
  makeLarkMessage,
}
