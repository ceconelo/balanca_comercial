from twitter import tweet_to_publish_with_image


def post():
    imgs = {
        'Exportações da agropecuária': 'png/exp-mensal-agropecuaria.png',
        'Exportações da indústria de transformação': 'png/exp-mensal-industria-de-transformacao.png',
        'Exportações da indústria extrativa': 'png/exp-mensal-industria-extrativa.png',
        'Importações da agropecuária': 'png/imp-mensal-agropecuaria.png',
        'Importações da indústria de transformação': 'png/imp-mensal-industria-de-transformacao.png',
        'Importações da indústria extrativa': 'png/imp-mensal-industria-extrativa.png'
    }

    released_date = None

    try:
        with open('datasets/last_download.txt', 'r') as f:
            released_date = f.readline()
    except FileNotFoundError as err:
        log.error(err)

    released_date = released_date.split('-')[1].strip()

    text = f'Atualização semanal da balança comercial brasileiraa\n{released_date}'

    query = 'Atualização semanal da balança comercial brasileiraa  -is:retweet'

    tweet_to_publish_with_image(text=text, query=query, imgs=imgs)


if __name__ == '__main__':
    post()
