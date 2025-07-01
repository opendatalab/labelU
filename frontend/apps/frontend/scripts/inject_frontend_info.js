const path = require('path');
const fs = require('fs');

// eslint-disable-next-line import/order
const { Octokit } = require('@octokit/rest');

const octokit = new Octokit({
  auth: process.env.PERSONAL_TOKEN,
});

const prettier = require('prettier');
const { getPackagesSync } = require('@manypkg/get-packages');
const minimist = require('minimist');

async function createCommit({ owner, repo, message, branch, files }) {
  const currentBranchRef = await octokit.git.getRef({
    owner,
    repo,
    ref: `heads/${branch}`,
  });

  const tree = [];

  for (const file of files) {
    const { data: blobData } = await octokit.git.createBlob({ owner, repo, content: file.content });

    tree.push({
      path: file.path,
      mode: '100644',
      type: 'blob',
      sha: blobData.sha,
    });
  }

  const { data: treeData } = await octokit.git.createTree({
    owner,
    repo,
    base_tree: currentBranchRef.data.object.sha,
    tree,
  });

  const { data: commitData } = await octokit.git.createCommit({
    owner,
    repo,
    message,
    tree: treeData.sha,
    parents: [currentBranchRef.data.object.sha],
  });

  await octokit.git.updateRef({
    owner,
    repo,
    ref: `heads/${branch}`,
    sha: commitData.sha,
  });
}

async function main() {
  const args = minimist(process.argv.slice(2));
  const [branch, nextVersion] = args._;
  const appPkgJson = require('../package.json');
  const workspace = path.join(__dirname, '../../../');
  const workspacePkgPath = path.join(workspace, 'package.json');
  const workspacePkgJson = require(workspacePkgPath);
  const pksPath = path.join(__dirname, '../package.json');
  const versions = {
    version: nextVersion || appPkgJson.version,
    deps: {},
  };

  console.log('next version is', nextVersion);

  const getCode = (info) => {
    return `
    (function () {
      window.__frontend = ${JSON.stringify(info, null, 2)};
    })();
    `;
  };

  const { packages } = getPackagesSync(workspace);

  packages.forEach((pkg) => {
    const pkgInFrontend = appPkgJson.dependencies[pkg.packageJson.name];
    if (pkgInFrontend) {
      versions.deps[pkg.packageJson.name] = pkg.packageJson.version;
    }
  });

  fs.writeFileSync(
    path.join(__dirname, '../dist/frontend_version.js'),
    prettier.format(getCode(versions), {
      singleQuote: true,
      trailingComma: 'all',
      proseWrap: 'never',
      endOfLine: 'lf',
      tabWidth: 2,
      printWidth: 120,
    }),
    'utf-8',
  );

  console.log('Inject frontend info success!');

  try {
    if (nextVersion && branch !== 'online') {
      appPkgJson.version = nextVersion;
      workspacePkgJson.version = nextVersion;
      fs.writeFileSync(path.join(__dirname, '../package.json'), JSON.stringify(appPkgJson, null, 2), 'utf-8');
      fs.writeFileSync(workspacePkgPath, JSON.stringify(workspacePkgJson, null, 2), 'utf-8');

      await createCommit({
        owner: 'opendatalab',
        repo: 'labelU-Kit',
        message: `chore: update frontend package.json version to ${nextVersion} [skip ci]`,
        files: [
          {
            content: JSON.stringify(appPkgJson, null, 2),
            path: path.relative(workspace, pksPath),
          },
          {
            content: JSON.stringify(workspacePkgJson, null, 2),
            path: path.relative(workspace, workspacePkgPath),
          },
        ],
        branch,
      });

      console.log('update package.json version success!');
    }
  } catch (e) {
    console.log('update package.json version failed!', e);
  }
}

main();
