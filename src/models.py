from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# association table for children<->parents
children = db.Table('children',
                db.Column('child_id', db.Integer, db.ForeignKey('member.id')),
                db.Column('parent_id', db.Integer, db.ForeignKey('member.id'))
                )

class Member(db.Model):
    """Node within the family tree."""

    __tablename__ = "member"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    parents = db.relationship('Member',
                          secondary=children,
                          primaryjoin=(children.c.child_id == id), 
                          secondaryjoin=(children.c.parent_id == id), 
                          backref=db.backref('children', lazy='dynamic'),
                          lazy='dynamic')
    
    def __repr__(self):
        return '<Member %r>' % self.name

    # member_type gets as paremeter the title for the Member: Child, Parent or Member(when you ask for a single member from wich relationships built on)
    def serialize(self, member_type):
        return {
            member_type : {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "age": self.age
            }
        }

    def getAllMembers():
        all_members = Member.query.order_by(Member.age.desc())
        all_members = list(map(lambda x: x.serialize("Member:"), all_members))
        return all_members

    def getParents(id):
        query_parents = db.session.query(children).filter(children.c.child_id == id).all() 
        # Pass "Parent" as parameter for serialize
        parents = list( map(lambda x: Member.query.get(x[1]).serialize("Parent"), query_parents))
        return parents

    def getChildren(id):
        query_children = db.session.query(children).filter(children.c.parent_id == id).all()
        # Pass "Child" as parameter for serialize
        child = list( map(lambda x: Member.query.get(x[0]).serialize("Child"), query_children))
        return child
    