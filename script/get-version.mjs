import path from 'path';
import fs from 'fs';
import got from 'got';

const COMMIT_URL = 'https://api.github.com/repos/GrantBirki/ghtrending/commits/main';

const getVersion = async function getVersion() {
    console.time(`Get version url ${COMMIT_URL}`);
    try {
        const response = await got(COMMIT_URL, {
            responseType: 'json',
        }).json();
        console.timeEnd(`Get version url ${COMMIT_URL}`);

        return response;
    } catch (responseError) {
        console.timeEnd(`Get version url ${COMMIT_URL}`);
        console.error(responseError);
    }

    return false;
};

(async () => {
    try {
        let response = false;

        response = await getVersion();

        console.log(response.sha);

        const version = {
            version: response.sha,
        }

        console.time('Write new data');
        fs.writeFileSync(path.join('src', 'data', 'version.json'), JSON.stringify(version, null, 4));
        console.timeEnd('Write new data');
    } catch (error) {
        console.error(error);
        fs.writeFileSync(path.join('src', 'data', 'version.json'), JSON.stringify(
            {
                version: 'unknown'
            }, null, 4
        ));
    }
})()


