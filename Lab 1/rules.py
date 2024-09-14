from production import IF, AND, THEN, OR, NOT

TOURIST_RULES = (
    # Earth Businessman
    IF(AND('(?x) wears business suit',
           '(?x) carries briefcase',
           '(?x) complains about gravity'),
       THEN('(?x) is an Earth Businessman')),

    # Mars Colonist
    IF(AND('(?x) wears practical jumpsuit',
           '(?x) has reddish skin tone',
           '(?x) is interested in agricultural exhibits'),
       THEN('(?x) is a Mars Colonist')),

    # Jovian Diplomat
    IF(AND('(?x) wears formal attire',
           '(?x) moves gracefully in low gravity',
           '(?x) discusses interplanetary politics'),
       THEN('(?x) is a Jovian Diplomat')),

    # Venusian Artist
    IF(AND('(?x) wears flamboyant clothing',
           '(?x) carries art supplies',
           '(?x) admires Luna-City architecture'),
       THEN('(?x) is a Venusian Artist')),

    # Belter Miner
    IF(AND('(?x) wears rugged work clothes',
           '(?x) has muscular build',
           '(?x) is interested in mineral exhibits'),
       THEN('(?x) is a Belter Miner')),

    # Loonie (Not a tourist)
    IF(AND('(?x) wears standard Luna-City attire',
           '(?x) moves naturally in low gravity',
           '(?x) knows local customs and locations'),
       THEN('(?x) is a Loonie')),

    # General tourist rule
    IF(OR('(?x) is an Earth Businessman',
          '(?x) is a Mars Colonist',
          '(?x) is a Jovian Diplomat',
          '(?x) is a Venusian Artist',
          '(?x) is a Belter Miner'),
       THEN('(?x) is a tourist')),

    # Not a tourist rule
    IF('(?x) is a Loonie',
       THEN(NOT('(?x) is a tourist')))
)