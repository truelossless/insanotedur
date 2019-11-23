const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

const Discord = require('discord.js');
const client = new Discord.Client();

const config = require('./config.json');
// config doit ressembler à:
// {
//     username: 'nom ent',
//     password: 'mdp ent',
//     token: 'token du bot discord',
//     frequency: 'intervalle de recherche en s'
// }

client.login(config.token);

client.on("message", async msg => {
    if(msg.content === 'yo') {
        msg.reply('brooo !');
    }
});

let map = {};
let browser, page;

(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();

    cycle(config.frequency * 1000, true);
})();

// requête toutes les x secondes
async function cycle(frequency, init) {

    try {
        await page.goto('https://cas.insa-rennes.fr/cas/login?service=https://ent.insa-rennes.fr/uPortal/Login%3FrefUrl%3D%2FuPortal%2Ff%2Finfosperso%2Fp%2FdossierAdmEtu.u19l1n17%2Fmax%2Frender.uP%253FpCp');
        await page.type('#username', config.username);
        await page.type('#password', config.password);
        await page.keyboard.press('Enter');
        await page.waitForNavigation();

    } catch (e) {
        // des erreurs de navigations se produiront surement
        console.warn('[catch] La page n\'a pas répondu.')
        if (init) setTimeout(() => cycle(frequency, true), frequency);
        else setTimeout(() => cycle(frequency, false), frequency);
        return;
    }

    let table;

    try {
        const element = await page.$('#portlet-DossierAdmEtu-tab2 table');
        table = await page.evaluate(element => element.outerHTML, element);
    } catch (e) {
        console.warn('[catch] La page HTML est mal formée.');
        if (init) setTimeout(() => cycle(frequency, true), frequency);
        else setTimeout(() => cycle(frequency, false), frequency);
        return;
    }

    const $ = cheerio.load(table);

    $('tr[style="border-bottom: 0.1em solid #B6CBD6"]').each((i, el) => {

        let topic = $(el).find('td[align=left]').text().trim();
        topic = topic.match(/-(.*)/)[1];

        const mark = $(el).find('td[align=right]').text();

        const markSubmitted = /[,0-9]+ \/ [0-9]{2}/.test(mark);

        if (init) {
            map[topic] = markSubmitted;
            if (markSubmitted) {
                console.log('Note existante pour ' + topic);
            }
        } else {
            if (!map[topic] && markSubmitted) {

                const emojis = ['😱', '😳', '😌', '🤕', '😇', '🤠', '😐'];
                const yeet = 'Nouvelle note pour: ' + topic + ' ' + emojis[Math.floor(Math.random()*emojis.length)];
                map[topic] = true;
                console.log(yeet);
                client.channels.find(ch => ch.name == 'notifs-partiels').send(yeet);
            }
        }
    });

    if (init) {
        console.log('\nInitialisation terminée.\n Recherche de nouvelles notes toutes les ' + frequency / 1000 + 's en cours ...');
    }

    await page.goto('https://cas.insa-rennes.fr/cas/login?service=https://cas.insa-rennes.fr/cas/logout');
    setTimeout(() => cycle(frequency, false), frequency);
}