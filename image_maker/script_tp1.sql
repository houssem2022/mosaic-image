

CREATE TABLE ENSEIGNANT(
code_e number  PRIMARY KEY ,
nom_e varchar(30) NOT NULL,
adr_e varchar(30),
tel_e varchar(10),
grade varchar(10) NOT NULL,
CONSTRAINT ck_1 grad CHECK IN ('PU', 'CERTIFIE','VACATAIRE','MC', 'MA','A', 'AUTRE' ),
)


CREATE TABLE ENTRPRISE (
code_ent number PRIMARY KEY ,
sigle_ent varchar(15) NOT NULL,
type_ent varchar(10),
adr_ent varchar(15),
tel_ent varchar(15),
CONSTRAINT ck_2 type_ent CHECK IN ('SII', 'PME', 'PMI', 'GRANDE', 'AUTRE' ),
)

CREATE TABLE ETUDIANT (
num_et number PRIMARY KEY ,
nom_et varchar(30) NOT NULL, 
adr_et varchar(30), 
tal_et varchar(10),
dip_et varchar(12) NOT NULL,
filiere_et varchar(20) NOT NULL,
nom_tuteur varchar(30),
code_ent number,
code_e number,
CONSTRAINT ck_3 dip_et CHECK IN ('LICENCE_PROF', 'DUT' ),
CONSTRAINT ck_4  filiere_et CHECK IN ('GEA', 'NFO', 'TC', 'INFO_COM' ),
CONSTRAINT fk_1  FOREIGN KEY (code_ent ) REFERENCES ENTRPRISE(code_ent),
CONSTRAINT fk_2  FOREIGN KEY (code_e ) REFERENCES ENSEIGNANT(code_e),
)

CREATE TABLE ETUDIANT (
code_ent number,
code_e number,
annee varchar(4),
CONSTRAINT pk_1 PRIMARY KEY (code_e,code_ent) ,
)
