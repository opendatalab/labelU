const process = require('node:process')

const { httpPost, makeLarkMessage } = require('./utils')

function format(input) {
  const rows = input.split('\n')
  const stringRows = []

  for (let i = 1; i < rows.length; i++) {
    // 空行或者换行符忽略
    if (rows[i].trim() === '' || rows[i].trim() === '\n') {
      continue
    }

    let row = rows[i].replace(/#/g, '')
    stringRows.push(row.trim())
  }

  return stringRows.join('\n')
}

async function main() {
  const releaseNotes = process.env.RELEASE_NOTES
  const frontendChangelog = `${process.env.CHANGELOG}`
  const botUrl = process.env.WEBHOOK_URL
  const releaseTag = process.env.NEXT_VERSION
  const pypiUrl = process.env.PYPI_URL

  console.log('url', botUrl)
  const frontendContent = frontendChangelog ? `\n\n**Frontend Changelog**\n${format(frontendChangelog)}` : ''

  try {
    const payload = makeLarkMessage(
      `LabelU@v${releaseTag}`,
      `${format(releaseNotes)}${frontendContent}`,
      '点击访问',
      pypiUrl,
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
