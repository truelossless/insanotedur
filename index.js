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

// on utilise un paramètre pour stopper le scrapping hors-partiel.
let idle = false;
let debug = false;

const stdin = process.openStdin();

stdin.addListener("data", d => {

    const input = d.toString().trim().split();
    
    if(input[0] === 'idle' && input.length === 1) {

        if(idle) {
            idle = false;
            console.log('Le bot est maintenant actif.');
        } else {
            idle = true;
            console.log('Le bot est passé en mode idle.');
        }
    } else if(input[0] === 'debug' && input.length === 1) {
        
        if(debug) {
            debug = false,
            console.log('Mode debug désactivé.');
        } else {
            debug = true;
            console.log('Mode debug activé.');
        }

    } else if(input[0] === 'msg' && input.length > 1) {

        let msg = '';
        for(let i=1; i<input.length; i++) {
            msg += input[i];
        }

    } else {
        console.log('Commandes valides: debug, idle, msg');
    }
});

(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();

    await scrape(true);
    console.log('\nInitialisation terminée.\nRecherche de nouvelles notes toutes les ' + config.frequency + 's en cours ...');
    
    setInterval(async () => {
        
        if(idle) {
            if(debug) {
                console.log('Requête annulée: idle');
            }    
            return;
        }


        const date = new Date();
        
        // on ne récupère pas les notes le samedi et le dimanche
        if(date.getDay() == 6 || date.getDay() == 0) {
            if(debug) {
                console.log('Requête annulée: week-end.');
            }
            return;
        }

        // on ne récupère pas les notes après 18h et avant 8h
        if(date.getHours() >= 18 || date.getHours() < 8) {
            if(debug) {
                console.log('Requête annulée: nuit.');
            }
            return;
        }
        
        if(debug) console.log('Nouvelle requête commencée.');
        await scrape(false);
        if(debug) console.log('Requete terminée.');

    }, config.frequency*1000);
})();



// requête toutes les x secondes
async function scrape(init) {

    try {
        await page.goto('https://cas.insa-rennes.fr/cas/login?service=https://cas.insa-rennes.fr/cas/logout');
        await page.goto('https://cas.insa-rennes.fr/cas/login?service=https://ent.insa-rennes.fr/uPortal/Login%3FrefUrl%3D%2FuPortal%2Ff%2Finfosperso%2Fp%2FdossierAdmEtu.u19l1n17%2Fmax%2Frender.uP%253FpCp');
        await page.type('#username', config.username);
        await page.type('#password', config.password);
        await page.keyboard.press('Enter');
        await page.waitForNavigation();

    } catch (e) {
        // des erreurs de navigations se produiront surement
        console.warn('[catch] La page n\'a pas répondu.');
        return;
    }

    let table;

    try {
        const element = await page.$('#portlet-DossierAdmEtu-tab2 table');
        table = await page.evaluate(element => element.outerHTML, element);
    } catch (e) {
        console.warn('[catch] La page HTML est mal formée.');
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
                const yeet = 'Nouvelle note pour: ' + topic + ' ' + emojis[Math.floor(Math.random()*emojis.length)] + '\n@everyone';
                map[topic] = true;
                console.log(yeet);
                client.channels.find(ch => ch.name == 'notifs-partiels').send(yeet);
            }
        }
    });
}