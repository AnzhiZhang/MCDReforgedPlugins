const core = require('@actions/core');
const execSync = require('child_process').execSync;
const pluginList = require('./plugin_list.json');
const tagList = execSync('git tag', {encoding: 'utf-8'}).trim().split('\n').reverse();

function isAffectReleaseLog(log) {
    return log.includes('fix') || log.includes('feat') || log.includes('!') || log.includes('Release-As: ');
}

let changedList = [];
for (let pluginKey in pluginList) {
    let pluginID = pluginList[pluginKey];
    let findTagFlag = false;
    for (let tagKey in tagList) {
        let tagName = tagList[tagKey];
        if (tagName.startsWith(pluginID)) {
            let gitLog = execSync(`git log ${tagName}...HEAD ${pluginID}`, {encoding: 'utf-8'});
            if (isAffectReleaseLog(gitLog)) {
                changedList.push(pluginID);
            }
            findTagFlag = true;
            break;
        }
    }
    if (!findTagFlag) {
        let gitLog = execSync(`git log ${pluginID}`, {encoding: 'utf-8'});
        if (isAffectReleaseLog(gitLog)) {
            changedList.push(pluginID);
        }
    }
}

function isAffectReleaseLog(log) {
    return log.includes('fix') || log.includes('feat') || log.includes('!') || log.includes('Release-As: ');
}

core.setOutput('changed', changedList.length > 0);
core.setOutput('plugins', JSON.stringify(changedList));
