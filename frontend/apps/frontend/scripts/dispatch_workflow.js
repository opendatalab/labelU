const https = require('https');

const minimist = require('minimist');
const { Octokit } = require('@octokit/rest');

const octokit = new Octokit({
  auth: process.env.PERSONAL_TOKEN,
});

function createPullRequest({ branchName, body, title = branchName, base = 'main' }) {
  if (!branchName) {
    return Promise.reject('branch name is not set');
  }

  console.log('Create a pull request');

  return octokit.rest.pulls
    .create({
      owner: 'opendatalab',
      repo: 'labelU-Kit',
      head: branchName,
      title,
      base,
      body,
    })
    .then(() => {
      console.log('Create a pull request success');
    });
}

function gitlabCiTrigger(nextVersion) {
  const version = `v${nextVersion}`;
  const url = `https://github.com/opendatalab/labelU-Kit/releases/download/${version}/frontend.zip`;
  const gitlabTriggerUrl = new URL(
    `https://gitlab.shlab.tech/api/v4/projects/${process.env.GI_LABELU_PROJECT_ID}/trigger/pipeline?token=${process.env.GL_TRIGGER_TOKEN}&ref=self-host`,
  );

  const formData = new URLSearchParams();

  formData.append('variables[frontend_url]', url);

  const options = {
    hostname: gitlabTriggerUrl.hostname,
    path: `${gitlabTriggerUrl.pathname}${gitlabTriggerUrl.search}`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  };

  const req = https.request(options, (res) => {
    if (res.statusCode < 300) {
      console.log('trigger labelu workflow success');
    } else {
      console.log('trigger labelu workflow failed', res);
    }
  });

  req.on('error', (e) => {
    console.log('trigger labelu workflow error', e);
  });
  req.write(formData.toString());
  req.end();
}

async function main() {
  const args = minimist(process.argv.slice(2));
  const [branch, nextVersion, releaseNotes] = args._;
  const version = `v${nextVersion}`;
  const url = `https://github.com/opendatalab/labelU-Kit/releases/download/${version}/frontend.zip`;

  if (branch === 'online') {
    gitlabCiTrigger(nextVersion);

    return;
  }

  const inputs = {
    version: version,
    branch: branch === 'release' ? 'main' : branch,
    release_type: 'fix',
    assets_url: url,
    changelog: releaseNotes,
  };

  console.log('inputs', inputs);

  octokit.actions
    .createWorkflowDispatch({
      owner: 'opendatalab',
      repo: 'labelU',
      workflow_id: 84825133,
      ref: branch === 'release' ? 'main' : branch,
      inputs,
    })
    .then((res) => {
      console.log(res);
      console.log('trigger labelu workflow success');
    })
    .catch((err) => {
      console.log('trigger labelu workflow failed', err);
    });

  await new Promise((resolve) => {
    setTimeout(async () => {
      createPullRequest({
        branchName: branch,
        body: releaseNotes,
        base: 'main',
        title: 'Update package version',
      }).catch((err) => {
        console.log(err);
      });
      resolve();
      // 避免 You have exceeded a secondary rate limit 问题
    }, 1000);
  });
}

main();
