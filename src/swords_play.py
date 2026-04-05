# [ DEBUG]
debug_mode = False
fast_start = False
auto_choose = False

# ---------------
#  | LIBRARIES |
# ---------------
import curses
from pyfiglet import figlet_format
from time import sleep
from random import randint, choice

# ---------------
#  | VARIABLES |
# ---------------
window = None

color_code = None
delay_dialogue = 0.03
fast_forward = False
auto_jump = False

tutorial = True
first_battle = True
fled = False

# ----------------
#  | CFUNCTIONS |
# ----------------
def clear_buffer():                                     # Clear do buffer de teclado, para não ter teclas restantes
    window.nodelay(True)  # Vai usar window.getch para consumir, no caso
    while window.getch() != -1:  # \ Enquanto não tiver teclas pressionadas (-1), 
        pass                     # / ele passa, consumindo elas.
    window.nodelay(False)

def cwait():                                            # Função de espera de input do usuário
    global fast_forward, auto_jump

    window.nodelay(False)
    while True:
        clear_buffer()
        key = window.getkey()
        match key:
            case 'z' | '\n': # z sai
                break
            case 'x':        # x é o de acelerar
                fast_forward = not fast_forward
            case 'c':        # c é para o autojump
                auto_jump = not auto_jump

def cprint(word='', end='\n'):                          # Função de print pelo curses, já com a cor
    window.addstr(word, color_code) # Não é possível usar o print, pois o print não sai na tela do terminal
    window.addstr(end)              # a entrada "end" de print, basicamente
    window.refresh()

def cinput(prompt='>  '):                               # Função de input pelo curses. Usa a mesma lógica do cprint
    clear_buffer()
    window.addstr('\n' + prompt, color_code)  # Pula uma linha, adiciona o prompt e a cor
    window.refresh()
    curses.curs_set(1)  # Mostra o cursor
    curses.echo()       # Faz com que o usuário controle, quando escrever sair no terminal
    uinput = window.getstr().decode().strip()  # Pega a string do usuário, com o getstr e decode para transformar em string
    curses.noecho()
    curses.curs_set(0)
    window.addstr('\n')  # Pula uma linha, para ficar mais bonito
    return uinput        # Retorna oq o usuário colocou

def ctitle(word, font='slant'):                         # Para criar o header (título de página) com a biblioteca pyfiglet
    window.clear()
    window.addstr(figlet_format(word, font), color_code)

def cmenu(header, description, options=[]):             # Menu interativo com o curses
    window.nodelay(False)
    clear_buffer()
    uselection = 0
    while True:
        ctitle(header)
        for line in description.splitlines():  # Pega os cortes de linha e já adiciona o espaço entre elas
            cprint(f'  {line}')
        cprint()
        if len(options) > 0:  # Se houver opções, entra no modo interativo
            for index, item in enumerate(options):
                if index == uselection:
                    cprint(f'> {item}')
                else:
                    cprint(f'  {item}')
        
            uinput = window.getkey()
            match uinput:
                case 'w' | 'KEY_UP':
                    uselection -= 1
                    if uselection == -1:
                        uselection = 0
                case 's' | 'KEY_DOWN':
                    uselection += 1
                    if uselection >= len(options):
                        uselection = len(options) - 1
                case 'z' | '\n':
                    cprint()                   # \ Pula uma linha
                    return options[uselection] # / e retorna o input do usuário
        else:  # Se não, sai do loop
            break

def csay(word, next_line=True):                         # Mostra cada letra de uma palavra
    global fast_forward, auto_jump

    window.nodelay(True)
    for ch in word:
        window.addstr(ch, color_code)
        try:
            key = window.getkey()
            match key:
                case 'x':
                    fast_forward = not fast_forward
                case 'c':
                    auto_jump = not auto_jump
        except curses.error:  # Se não houver input válido, passa
            pass              # É preciso por conta do jeito que o getkey funciona
        window.refresh()
        sleep(delay_dialogue if not fast_forward else delay_dialogue/2)
    if next_line:  # Se tiver eu pedir para ir para a próxima linha, vai
        window.addstr('\n')
    if not auto_jump:
        cwait()

#  FUNCTIONS  #
def debug(text):
    if debug_mode:
        cprint(f'[DEBUG] {text}')

def roll(dices=1, faces=20, advantage=False):  # Roda certo número de dados, com número de faces e vantagem
    rolls = []  # Cria uma lista vazia para os resultados
    if advantage:  # Se tiver vantagem, ganha +1 dado
        dices += 1

    if dices > 0:  # Se tiver dados, roda o tanto deles com base nas faces e pega o máximo dos resultados
        for i in range(dices):
            rolls.append(randint(1, faces))
        debug(f'{dices}d{faces} -> {rolls}, {max(rolls)}')
        return max(rolls)
    elif dices in (-1, 0):         # Se for -1 ou 0, roda só dois dados, só que pega o menor
        rolls.append(randint(1, faces))
        rolls.append(randint(1, faces))
        debug(f'{dices}d{faces} -> {rolls}, {min(rolls)}')
        return min(rolls)
    else:                          # Se for muito pequeno, só retorna 0, no caso, falha automaticamente
        debug('RETURNED 0!!')
        return 0

def change_hp(amount):                                  # Muda a vida do personagem, fazendo a verificação para não passar da vida total
    character["Health"] += amount
    if character["Health"] > character["Max Health"]:
        character["Health"] = character["Max Health"]

# ---------------
#  | CHARACTER |
# ---------------
character = {
    "Name": '',
    "Race": '',
    "Class": '',
    "Experience": 0,
    "Level": 1,

    "Health": 0,
    "Max Health": 0,
    "Aether": 0,

    "Defense": 0,
    "Damage": 0,

    "Strength": 1,
    "Dexterity": 1,
    "Constitution": 1,
    "Wisdom": 1,
    "Charisma": 1,

    "Réis": 0,
}
character_stored = {}
character_skills = []

# ----------
#  | ITEM |
# ----------
def inventory(mode=1):              # Mostrar inventário ou usar itens
    if mode == 1:  # Modo de visualização
        if len(character_stored) == 0:
            cmenu('Inventory',
                  'Seu inventário está vazio.',
                  ['Continuar'])
            
    elif mode == 2: # Modo de uso
        pass

def health_potion(size=1, mode=1):  # Adiciona uma poção ao inventário com base no tamanho
    small  = "Small Health Potion"
    medium = "Medium Health Potion"
    great  = "Great Health Potion"
    
    if mode == 1:
        match size:
            case 1:
                if small not in character_stored:
                    character_stored[small] = {
                        "Description": "Uma pequena poção de cura. Restaura 4 de vida.",
                        "Quantity": 1,
                        "Heal": 4
                    }
                else:
                    character_stored[small]["Quantity"] += 1
            case 2:
                if medium not in character_stored:
                    character_stored[medium] = {
                        "Description": "Uma média poção de cura. Restaura 10 de vida.",
                        "Quantity": 1,
                        "Heal": 10
                    }
                else:
                    character_stored[medium]["Quantity"] += 1
            case 3:
                if great not in character_stored:
                    character_stored[great] = {
                        "Description": "Uma grande poção de cura. Restaura 20 de vida.",
                        "Quantity": 1,
                        "Heal": 20
                    }
                else:
                    character_stored[great]["Quantity"] += 1
            
    elif mode == 2:
        match size:
            case 1:
                character_stored[small]["Quantity"] -= 1
                if character_stored[small]["Quantity"] == 0:
                    character_stored.remove(small)
            case 2:
                character_stored[medium]["Quantity"] -= 1
                if character_stored[medium]["Quantity"] == 0:
                    character_stored.remove(medium)
            case 3:
                character_stored[great]["Quantity"] -= 1
                if character_stored[great]["Quantity"] == 0:
                    character_stored.remove(great)

# -------------
#  | ENEMIES |
# -------------
enemy = {  # Dicionário base do inimigo, que pode ser mudado para os valores das funções abaixo
    "Name": '',
    "Health": 0,
    "Max Health": 0,
    "Defense": 0,
    "Experience": 0,
    "Réis": 0
}
enemy_actions = {}

def wolf():  # Muda o dicionário do inimigo para um lobo
    global enemy, enemy_actions

    enemy = {
        "Name": "Lobo",
        "Health": 6,
        "Max Health": 6,
        "Defense": 1,
        "Experience": 5,
        "Réis": 1
    }
    
    enemy_actions = {
        "Arranhão": {
            "Damage": 4,
            "Bonus":  2
        },
        "Mordida": {
            "Damage": 5,
            "Bonus": 1
        }
    }

def goblin():
    global enemy, enemy_actions

    enemy = {
        "Name": "Goblin",
        "Health": 8,
        "Max Health": 8,
        "Defense": 2,
        "Experience": 10,
        "Réis": 4
    }
    enemy_actions = {
        "Porretada": {
            "Damage": 6,
            "Bonus":  1
        },
        "Flechada": {
            "Damage": 5,
            "Bonus": 2
        }
    }

# -----------
#  | START |
# -----------
def start():
    while True:
        start = cmenu('Swords Play',
                      'Pronto para a aventura?',
                      ['Jogar', 'Configurações', 'Créditos'])
        match start:
            case 'Jogar':
                break
            case 'Configurações':
                settings()
            case 'Créditos':
                credits()

def settings():
    global tutorial

    while True:
        setting = cmenu('Settings',
                        'Para ativar ou desativar uma função, digite o número correspondente.',
                        ['Voltar', f'[ON]  Tutorial' if tutorial else '[OFF] Tutorial', 'Mudar cor do Texto'])
        match setting:
            case 'Voltar':
                break
            case  '[ON]  Tutorial' | '[OFF] Tutorial':
                tutorial = not tutorial
            case 'Mudar cor do Texto':
                color_choice()

def color_choice():
    global color_code

    while True:
        color_choice = cmenu('Color Choice',
                             'Escolha uma cor para o texto',
                             ['Voltar', 'Branco', 'Verde', 'Vermelho', 'Azul', 'Amarelo', 'Ciano', 'Magenta'])
        match color_choice:
            case 'Voltar':
                break
            case 'Branco':
                color_code = curses.color_pair(1)
            case 'Verde':
                color_code = curses.color_pair(2)
            case 'Vermelho':
                color_code = curses.color_pair(3)
            case 'Azul':
                color_code = curses.color_pair(4)
            case 'Amarelo':
                color_code = curses.color_pair(5)
            case 'Ciano':
                color_code = curses.color_pair(6)
            case 'Magenta':
                color_code = curses.color_pair(7)

def credits():
    ctitle('Credits')
    csay('Primeiramente, claro, queria dar créditos a mim, Sarah Aurora.')
    csay('Estou trabalhando nesse projeto acho que desde o dia 10/7/2025.')
    csay('Muitas dificuldades foram enfrentadas, principalmente o mal uso de IA.')
    csay('Imagino que o projeto ainda não esteja pronto.')
    csay('Claro, sempre irei encontrar algum defeito no código, não sou perfeita.')
    csay('O importante é que esse é o maior projeto que já fiz.')
    csay('Nenhum projeto meu teve mais que 300 linhas.')
    csay('No momento em que escrevo isso, já tenho mais de 800, e sempre irá aumentar.\n')
    csay('Parando de falar de mim, vamos falar dos "Beta-Testers", pessoas que testaram o jogo antes que muitos.')
    csay('Para proteger a identidade deles, vou chamar alguns deles por apelidos.')
    csay('Em ordem de quem testou primeiro, temos:\n')
    csay('- "Vini", amigo meu da escola. Me ajudou bastante dando ideias.')
    csay('- "Dri", meu melhor amigo. Me ajudou dando ideias também.')
    csay('- "Matt", outro amigo meu da escola.')
    csay('- "Will", amigo meu da escola.')
    csay('- "Cyan", amigo meu da escola.')
    csay('- "Robinho", best meu da escola.')
    ('- "Veruska", minha atual namorada.')
    csay('- "Tonho", que testou muito meu jogo e acompanhou seu desenvolvimento.\n')
    csay('E por último (e mais importante) temos Junko Gabryel.')
    csay('Literalmente me acompanhou no código e me deu muitas dicas sobre programação.')
    csay('Abraços, Gabe... sem você e suas dicas, esse projeto não seria o mesmo. <3\n')
    csay('Enfim... é isso.')
    csay('Muito obrigada por me ouvir (ou ler) até o final.\n')
    csay('--  Fim! B_)  --')

# ------------------------
#  | CHARACTER CREATION |
# ------------------------
def disclaimer():
    if tutorial:
        z = '<Z> continua um diálogo após terminar.'
        x = '<X> acelera um diálogo.'
        c = '<C> ativa o diálogo automático.'
        cmenu('Controls',
              f'{z}\n{x}\n{c}',
              ['Continuar'])
    ctitle('Disclaimer')
    csay('Olá, Jogador.')
    csay('Meu nome é Sarah Aurora. Sou a criadora deste projeto, chamado de Swords Play.\n')
    csay('Este projeto é um RPG de Texto de minha autoria, inspirado em RPGs clássicos.')
    csay('Conforme esperado, suas ações terão um certo peso na história.\n')
    csay('Tenha cuidado. Ao longo do caminho, você encontrará inimigos.')
    csay('Se você morrer, perderá todo o seu progresso. ', False)
    csay('Tome cuidado.\n')
    csay('Algumas mecânicas podem parecer um pouco confusas no começo...')
    csay('Mas não se preocupe, você se acostumará com o tempo.\n')
    csay('Enfim. Era isso que eu tinha a te dizer.\n')
    csay('Boa sorte, Desbravador.')

def choose_name():
    ctitle('Name')
    cprint('Qual será seu nome?\n(Deixe em branco para usar o nome padrão "Desbravador")')
    name = cinput('>  ').title()
    if name == '':
        character["Name"] = "Desbravador"
        csay('Você não escolheu um nome...')
        csay('Você não quer ter um nome??')
        csay('Tá... Vou te chamar de "Desbravador" então.\n')
    else:
        character["Name"] = name.title()
        csay('Que nome esbelto!')
        csay('Queria eu ter um nome... HAHA!!\n')

def choose_race():
    race = cmenu('Race',
                 'Qual será sua raça?',
                 ['Humano  (+1 Carisma)', 'Elfo    (+1 Sabedoria)', 'Anão    (+1 Constituição)'])
    match race:
        case 'Humano  (+1 Carisma)':
            csay('Você escolheu Humano!\n')
            choose('human')
        case 'Elfo    (+1 Sabedoria)':
            csay('Você escolheu Elfo!\n')
            choose('elf')
        case 'Anão    (+1 Constituição)':
            csay('Você escolheu Anão!\n')
            choose('dwarf')
            

def choose_class():
    chr_class = cmenu('Class',
                 'Qual será sua classe?',
                 ['Guerreiro (+1 Força)', 'Arqueiro  (+1 Destreza)', 'Mago      (+1 Sabedoria)'])
    
    match chr_class:
        case 'Guerreiro (+1 Força)':
            csay('Você escolheu Guerreiro!\n')
            choose('knight')
        case 'Arqueiro  (+1 Destreza)':
            csay('Você escolheu Arqueiro!\n')
            choose('archer')
        case 'Mago      (+1 Sabedoria)':
            csay('Você escolheu Mago!\n')
            choose('mage')

def choose(thing):
    thing = thing.strip().lower()
    match thing:
        case 'human':
            character["Race"] = "Humano"
            character["Charisma"] += 1
        case 'elf':
            character["Race"] = "Elfo"
            character["Wisdom"] += 1
        case 'dwarf':
            character["Race"] = "Anão"
            character["Constitution"] += 1

        case 'knight':
            character["Class"]    =  'Guerreiro'
            character["Strength"] += 1
            character["Damage"]   =  3
            character["Defense"]  =  2
        case 'archer':
            character["Class"]     =  'Arqueiro'
            character["Dexterity"] += 1
            character["Damage"]    =  3
            character["Defense"]   =  1
        case 'mage':
            character["Class"]     =  'Mago'
            character["Wisdom"]    += 1
            character["Damage"]    =  2
            character["Defense"]   =  0


def ready():
    while True:
        ready_or_not = cmenu('Ready?',
                             'Temos tudo para começarmos?',
                             ['Sim (continua)', 'Não (volta para as escolhas)'])
        match ready_or_not:
            case 'Sim (continua)':
                csay('Ótimo! Vamos começar!')
                break
            case 'Não (volta para as escolhas)':
                csay('Vamos voltar para as escolhas!')
                choose_name()
                choose_race()
                choose_class()

def character_creation():
    ctitle('Cosmic Forge')
    csay('Olá, Desbravador!')
    csay('Bem-vindo à OFICINA CÓSMICA!')
    csay('Aqui é... meio vazio. Mas eu consigo fazer coisas mágicas por aqui!')
    csay('Enfim... Vamos criar sua representação!')
    csay('Qual será seu nome?')
    choose_name()
    csay('Enfim, este é um mundo místico...')
    csay('Nele, você pode escolher ser coisas incríveis!')
    csay('O que você vai ser?')
    csay('Humano? ', False)
    csay('Elfo? ', False)
    csay('Alguma outra raça?')
    choose_race()
    csay('Enfim...')
    csay('Agora que você escolheu uma raça, precisamos saber no que você é bom, não é?')
    csay('Você quer uma espada? ', False)
    csay('Um arco? ', False)
    csay('Um cajado???')
    csay('Vamos! Eu sei que é difícil escolher só um!')
    choose_class()
    csay('Agora que temos tudo, vamos começar a aventura!')
    csay('Você está pronto?')
    ready()

def show_status():
    text = f'Nome:        {character["Name"]}\n' \
           f'Raça:        {character["Race"]}\n' \
           f'Class:       {character["Class"]}\n\n' \
           f'Vida:      {character["Health"]}/{character["Max Health"]}\n' \
           f'Defesa:    {character["Defense"]}\n' \
           f'Dano Base: {character["Damage"]}\n\n' \
           f'Força:         {character["Strength"]}\n' \
           f'Destreza:      {character["Dexterity"]}\n' \
           f'Constituição:  {character["Constitution"]}\n' \
           f'Sabedoria:     {character["Wisdom"]}\n' \
           f'Carisma:       {character["Charisma"]}\n\n' \
           f'Réis: {character["Réis"]}\n\n'
    cmenu('Status',
          text,
          ['Continuar'])

# -------------
#  | HISTORY |
# -------------
def history():
    ctitle('History')
    csay('Há muito tempo, dois dragões reinavam sobre a terra.')
    csay('Dragões esses muitos poderosos. Não simples, mas sim anciões.')
    csay('O primeiro era o de fogo. Ele cuidava das criações, mas não haviam vida.')
    csay('Ele era apenas a forja. Não detinha a força da vida.')
    csay('Seguindo isso, uma outra entidade aparece, o Dragão de Água.')
    csay('Ele cuidava cuidava da vida, surgindo o mundo que conhecemos.\n')
    csay('Entretanto, milênios depois, surgiu um desequilíbrio entre essas duas entidades.')
    csay('O Dragão de Fogo, com sua fúria, começou a consumir o mundo.')
    csay('O Dragão de Água, com sua calma, tentava conter o fogo.\n')
    csay('Um portal foi aberto. ', False)
    csay('O mundo está em colapso. ', False)
    csay('O inferno está cheio.\n')
    csay('Você adora uma grande aventura, claro. Você não dispensaria essa oportunidade.')
    csay('Você se devotou ao Rei de Xannegar.')
    csay('Você jurou conter esse mal, e vai trabalhar fielmente por isso.\n')
    csay('Sua primeira missão é ir até Xannegar para procurar um grupo.')
    csay('Boa sorte.')
    ctitle('Village')
    csay('Você se encontra em sua vila de origem.')
    csay('Você tem um objetivo em mente: Ir para a Capital, Xannegar.')
    csay('Na sua vila não tem ninguém pra te ajudar por ser muito pequena.')
    csay('A única coisa que lhe restava era pegar carona.\n')
    csay('Você pegou carona em uma carroça de um comerciante com o destino em comum.')
    csay('Você pediu educamente, e claro que ele deixou.')
    csay('Junto com você, temos frutas e outros alimentos. Fome não será um problema.')
    csay('O tempo da viagem será de mais ou menos de 2 dias.\n')
    csay('Desejo boa sorte. Se seu personagem morrer, saiba que a aventura termina.')
    if tutorial:
        ctitle('Xannegar Way')
        csay('Você está a caminho de Xannegar.')
        csay('Para chegar lá, será necessário algum tempo.')
        csay('Será dividido em momentos, mais especificamente em 4 momentos.')
        csay('Serão dia e noite, do primeiro e segundo dia.\n')
        csay('Realizar qualquer ação fará o tempo passar de qualquer maneira.')
        csay('Além disso, ainda há chance de encontrar monstros no caminho.\n')
        csay('Desejo boa sorte.')

# -- Xannegar Way --
def xannegar_way():
    moment = 1
    hungry = 0
    sleep = 0

    while True:
        match moment:
            case 1: text_moment = '[MOMENTO] É manhã do primeiro dia.'
            case 2: text_moment = '[MOMENTO] É noite do primeiro dia.'
            case 3: text_moment = '[MOMENTO] É manhã do segundo dia.'
            case 4: text_moment = '[MOMENTO] É noite do segundo dia. Talvez amanhã você chegue.'
            case 5: break

        match hungry:
            case 0: text_hungry = '[FOME] Você está satisfeito. Não é preciso comer.'
            case 1: text_hungry = '[FOME] Você está começando a sentir fome.'
            case 2: text_hungry = '[FOME] Você sente fome. Continuar assim vai te fazer perder vida.'
            case 3: text_hungry = '[FOME] Você sente MUITA fome. Você precisa comer URGENTEMENTE.'

        match sleep:
            case 0: text_sleep = '[SONO] Você não sente sono. Não é preciso dormir.'
            case 1: text_sleep = '[SONO] Você ainda não sente sono. Ainda não é preciso dormir.'
            case 2: text_sleep = '[SONO] Você sente sono. É melhor dormir essa noite.'
            case 3: text_sleep = '[SONO] Você sente MUITO sono. Você precisa dormir URGENTEMENTE.'

        action = cmenu('Xannegar Way',
                       f'{text_moment}\n{text_hungry}\n{text_sleep}',
                       ['Nada', 'Comer', 'Dormir'])
        match action:
            case 'Nada':
                nothing = roll(1, 3)
                match nothing:
                    case 1: csay('Você apenas passa o tempo olhando para cima, fazendo nada de especial.')
                    case 2: csay('Você conversa com o dono da carroça para passar o tempo.')
                    case 3:
                        csay('Você vasculha um pouco sua bolsa, tentando passar o tempo.')
                        item = roll(character['Wisdom'])
                        if item >= 16:
                            csay('Você encontra uma poção de vida perdida dentro da sua bolsa.')
                            csay('Você guarda ela em um canto mais fácil de encontrar.')
                            health_potion()
                        else:
                            csay('Não há nada que te chame atenção.')
                hungry += 1
                sleep += 1
            case 'Comer':
                csay('Você come algo.')
                csay('Você não sente mais fome.')
                change_hp(2)
                hungry = 0
                sleep += 1
            case 'Dormir':
                hp_up = roll(1, character["Health"]/2)
                change_hp(hp_up)

                csay('Você dorme por esse momento.')
                csay('Você não sente mais sono.')
                csay(f'Além disso, você recupera {hp_up} de vida, ficando com {character["Health"]}.')
                sleep = 0
                hungry += 1

        moment += 1
        cprint()
        if not first_battle:
            battle_chance = roll(1, 2)
            if battle_chance == 1:
                enemy = roll(1, 3)
                if enemy <= 2:
                    csay('Você encontra um inimigo no caminho!')
                    csay('Parece que é um lobo!')
                    csay('Prepare-se para a batalha!')
                    wolf()
                else:
                    csay('Você encontra um inimigo no caminho!')
                    csay('Parece que é um goblin!')
                    csay('Prepare-se para a batalha!')
                    goblin()
                battle()
            else:
                csay('Não acontece mais nada de especial.')
        else:
            csay('Você encontra um inimigo no caminho!')
            csay('Parece que é um lobo!')
            csay('Prepare-se para a batalha!')
            wolf()
            fbattle()
            

def xannegar():
    pass

# ------------
#  | BATTLE |
# ------------
def fbattle():
    global first_battle

    first_battle = False
    if tutorial and not fast_start:
        ctitle('First Battle')
        csay('Essa é a sua primeira batalha!')
        csay('Você vai enfrentar um lobo!\n')
        csay('Você terá sua vez de agir, e depois o inimigo terá a vez dele.')
        csay('Você pode realizar ações como atacar, usar habilidades, usar itens ou fugir.\n')
        csay('Para usar habilidades, você precisará de Aether.')
        csay('Enquanto espera suas habilidades, tente conseguir Aether.')
        csay('Atacar normalmente com espada ou arco te dá 20% de Aether.')
        csay('Com cajado, você ganhará dá 35% de Aether.\n')
        csay('A batalha termina quando o inimigo ou você morrer.')
        csay('Você receberá experiência ao derrotar o inimigo, aumentando seu nível.')
        csay('Quanto maior seu nível, mais forte você fica.\n')
        csay('Além disso, você ganhará dinheiro.')
        csay('Dinheiro pode ser usado para comprar equipamentos, itens, comida...')
        csay('Tudo isso pode ser comprado em Xannegar.\n')
        csay('Enfim, é isso que eu tinha a te dizer.')
        csay('Boa sorte! B)')
    battle()

# -- Loop's --
def battle():
    global fled
    
    while enemy["Health"] > 0 and character["Health"] > 0:
        your_turn()
        if enemy["Health"] > 0:
            enemy_turn()
    
    if fled:
        fled = False
        cmenu('Run Away',
              'Você conseguiu fugir da batalha!',
              ['Continuar'])
    else:
        victory_defeat()


def your_turn():
    your_status  = f'Você:    {character["Name"]} ({character["Health"]}/{character["Max Health"]}), {character["Aether"]}% Aether'
    enemy_status = f'Inimigo: {enemy["Name"]} ({enemy["Health"]}/{enemy["Max Health"]})'

    action = cmenu('Battle!',
                   f'{your_status}\n{enemy_status}',
                   ['Atacar', 'Habilidade  (WIP)', 'Item  (WIP)', 'Fugir'])
    match action:
        case 'Atacar':
            attack()
        case 'Habilidade':
            skill()
        case 'Item':
            item()
        case 'Fugir':
            run()

def enemy_turn():
    name, index = choice(list(enemy_actions.items()))

    csay(f'\nO {enemy["Name"]} prepara para te atacar...')
    if roll() >= 4:
        damage = roll(1, index["Damage"]) + index["Bonus"]
        character["Health"] -= damage
        csay('Ele te acerta.')
        csay(f'Ele avança, usando {name} e causando {damage} de dano.')
    else:
        csay(f'Ele erra o golpe.')
        csay(f'Ele tentou usar {name}, mas você se esquivou.')

def victory_defeat():
    if enemy["Health"] <= 0:
        character["Experience"] += enemy["Experience"]
        character["Réis"] += enemy["Réis"]

        ctitle('Victory!')
        cprint(f'Experiência: {character["Experience"]} (+{enemy["Experience"]})')
        cprint(f'Réis:        {character["Réis"]} (+{enemy["Réis"]})\n')
        csay(f'Você venceu um {enemy["Name"]}!')
        csay('Parabéns! Vencer uma batalha é sempre um desafio.')
    
    elif character["Health"] <= 0:
        ctitle('Defeat...')
        csay('Como um passe de mágica... ', False)
        csay('Você morre.\n')
        csay('De fato, é complicado. ', False)
        csay('Nem imagino como seria perder tanto tempo de progresso.')
        csay('Claro, sempre tem uma forma de reiniciar.')
        csay('Aqui, não é diferente.\n')
        csay('Você perdeu todo seu progresso.')
        csay('Ainda te dou uma chance...\n')
        csay('Você deseja continuar?')
        
        retry = cmenu('Retry?',
              'Você quer continuar?',
              ['Sim!', 'Não.'])
        
        if retry == 'Sim':
            ctitle('Retry?')
            cprint('  Você quer continuar?\n')
            cprint('  Sim!')
            cprint('> Não.')
            sleep(5)
            exit()
        else:
            exit()

# -- Actions --
def attack():
    chr_class = character["Class"]

    csay('Você tenta atacar o inimigo...')
    match chr_class:
        case "Guerreiro":
            attack_roll = roll(character["Strength"])
        case "Arqueiro":
            attack_roll = roll(character["Dexterity"])
        case "Mago":
            attack_roll = roll(character["Wisdom"])
    
    if attack_roll >= 4:
        damage = roll(1, character["Damage"])
        match chr_class:
            case "Guerreiro":
                damage += character["Strength"]
            case "Arqueiro":
                damage += character["Dexterity"]
            case "Mago":
                damage += character["Wisdom"]
        character["Aether"] += 35 if chr_class == 'Mago' else 30
        if character["Aether"] > 100:
            character["Aether"] = 100

        enemy["Health"] -= damage
        csay(f'E acerta, causando {damage} de dano!')
        csay(f'Você recebe {'35%' if chr_class == "Mago" else '20%'} de Aether, ficando com {character["Aether"]}%!')
    else:
        character["Aether"] += 15
        csay('Mas erra!')
        csay(f'Felizmente, você ainda recebe 15% de Aether, ficando com {character["Aether"]}%.')

def skill():
    pass

def item():       
    pass

def run():
    global fled

    csay('Você tenta fugir...')
    try_run = roll(character["Dexterity"])
    if try_run >= 8:
        csay('Você consegue fugir!')
        enemy["Health"] = 0
        fled = True
    else:
        csay('Você não consegue fugir!')

# ----------
#  | MAIN |
# ----------
def main(stdscr):
    """
    Função principal, que é indispensável quando usa a biblioteca curses.

    É preciso transformar a var global window para stdscr, entrada de tela do curses
    É necessário para as funções serem definidas,
    (não iria dar, por conta que window não estaria definido e não seria usado como objeto)
    e quando usadas, sempre sairem na mesma tela (stdscr)
    quando chama uma função, ela está definida como stdscr
    """
    global window, color_code
    window = stdscr  


    stdscr.scrollok(True) # Faz o curses poder reconhecer o \n na string. Normalmente, não reconhece
    curses.curs_set(0)    # Faz o cursor desaparecer.

    curses.start_color()  # Inicia o modo de cor do curses
    curses.init_pair(1, curses.COLOR_WHITE,   curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN,   curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED,     curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN,    curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    color_code = curses.color_pair(3) # Inicia no par 2, verde

    if not fast_start:
        start()
        disclaimer()
        character_creation()
        character["Health"]     = 10 + character["Constitution"] * 2
        character["Max Health"] = character["Health"]
        show_status()
        history()
        xannegar_way()
        xannegar()
    else:
        start()
        character["Name"] = 'Desbravador'
        if auto_choose:
            choose('elf')
            choose('mage')
        else:
            choose_race()
            choose_class()
        character["Health"]     = 10 + character["Constitution"] * 2
        character["Max Health"] = character["Health"]
        show_status()
        xannegar_way()


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass
