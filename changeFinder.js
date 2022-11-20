const core = require('@actions/core');
const execSync = require('child_process').execSync;
const pluginList = require('./plugin_list.json');
const tagList = execSync('git tag', {encoding: 'utf-8'}).trim().split('\n').reverse();

let changedList = [];
for (let pluginKey in pluginList) {
    let pluginID = pluginList[pluginKey];
    let findTagFlag = false;
    for (let tagKey in tagList) {
        let tagName = tagList[tagKey];
        if (tagName.startsWith(pluginID)) {
            let gitLog = execSync(`git log ${tagName}...HEAD --oneline ${pluginID}`, {encoding: 'utf-8'});
            if (gitLog.includes('fix') || gitLog.includes('feat') || gitLog.includes('!')) {
                changedList.push(pluginID);
            }
            findTagFlag = true;
            break;
        }
    }
    if (!findTagFlag) {
        let gitLog = execSync(`git log --oneline ${pluginID}`, {encoding: 'utf-8'});
        if (gitLog.includes('fix') || gitLog.includes('feat') || gitLog.includes('!')) {
            changedList.push(pluginID);
        }
    }
}

core.setOutput('changed', changedList.length > 0);
core.setOutput('plugins', JSON.stringify(changedList));
