const process = require('node:process')

const https = require('node:https')

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

async function main() {
  const botUrl = process.env.WEBHOOK_URL

  console.log('url', botUrl)

  try {
    const payload = makeLarkMessage(
      `LabelU 文档已更新`,
      "",
      '点击访问',
      "https://opendatalab.github.io/labelU/",
    )

    // 将 release 信息通过 POST 请求发送到指定 URL
    console.log(JSON.stringify(payload))
    // return
    const postResponse = await httpPost(botUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    }, payload)

    const responseBody = JSON.parse(postResponse)

    if (responseBody.code > 0) {
      throw new Error(`POST 请求失败: ${responseBody.msg}`)
    }

    console.log('Release 信息已成功发送')
  }
  catch (error) {
    console.error('发生错误:', error)
    process.exit(1)
  }
}

main()